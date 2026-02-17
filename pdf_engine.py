"""PDF processing engine - all PDF operations."""

import asyncio
import io
import zipfile
import math
from typing import Optional
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
from PIL import Image
from models import PDFOptions, CompressionQuality, WatermarkPosition


# Singleton browser instance
_browser = None
_playwright = None


async def get_browser():
    """Get or create a shared browser instance."""
    global _browser, _playwright
    if _browser is None or not _browser.is_connected():
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
    return _browser


async def close_browser():
    """Close browser on shutdown."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()
    _browser = None
    _playwright = None


def _build_pdf_params(options: PDFOptions) -> dict:
    """Build Playwright PDF parameters from options."""
    params = {
        "format": options.format,
        "margin": {
            "top": options.margin.top,
            "right": options.margin.right,
            "bottom": options.margin.bottom,
            "left": options.margin.left,
        },
        "landscape": options.landscape,
        "print_background": options.print_background,
        "scale": options.scale,
    }
    if options.header_html:
        params["display_header_footer"] = True
        params["header_template"] = options.header_html
    if options.footer_html:
        params["display_header_footer"] = True
        params["footer_template"] = options.footer_html
    if options.header_html or options.footer_html:
        params["display_header_footer"] = True
        if not options.header_html:
            params["header_template"] = "<span></span>"
        if not options.footer_html:
            params["footer_template"] = "<span></span>"
    return params


async def html_to_pdf(html: str, options: PDFOptions, add_watermark: bool = False) -> bytes:
    """Convert HTML string to PDF."""
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.set_content(html, wait_until="networkidle", timeout=30000)
        pdf_params = _build_pdf_params(options)
        pdf_bytes = await page.pdf(**pdf_params)
    finally:
        await page.close()

    if add_watermark:
        pdf_bytes = _add_free_tier_watermark(pdf_bytes)

    return pdf_bytes


async def url_to_pdf(url: str, options: PDFOptions, add_watermark: bool = False) -> bytes:
    """Convert URL to PDF."""
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        pdf_params = _build_pdf_params(options)
        pdf_bytes = await page.pdf(**pdf_params)
    finally:
        await page.close()

    if add_watermark:
        pdf_bytes = _add_free_tier_watermark(pdf_bytes)

    return pdf_bytes


def _add_free_tier_watermark(pdf_bytes: bytes) -> bytes:
    """Add 'EditPDFree.com - Free Tier' watermark to all pages."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        media_box = page.mediabox
        page_width = float(media_box.width)
        page_height = float(media_box.height)

        # Create watermark
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        c.setFont("Helvetica", 10)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.5))
        c.drawString(10, 10, "Generated with EditPDFree.com API - Free Tier")
        c.save()
        packet.seek(0)

        watermark_reader = PdfReader(packet)
        page.merge_page(watermark_reader.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def merge_pdfs(pdf_files: list[bytes], add_watermark: bool = False) -> bytes:
    """Merge multiple PDF files into one."""
    writer = PdfWriter()

    for pdf_data in pdf_files:
        reader = PdfReader(io.BytesIO(pdf_data))
        for page in reader.pages:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    result = output.getvalue()

    if add_watermark:
        result = _add_free_tier_watermark(result)

    return result


def compress_pdf(pdf_data: bytes, quality: CompressionQuality, add_watermark: bool = False) -> bytes:
    """Compress a PDF file."""
    reader = PdfReader(io.BytesIO(pdf_data))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Apply compression
    if quality == CompressionQuality.low:
        # Maximum compression
        for page in writer.pages:
            page.compress_content_streams()
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    elif quality == CompressionQuality.medium:
        for page in writer.pages:
            page.compress_content_streams()
        writer.compress_identical_objects(remove_identicals=True)
    else:
        # High quality = minimal compression
        for page in writer.pages:
            page.compress_content_streams()

    # Handle images based on quality
    quality_map = {
        CompressionQuality.low: 30,
        CompressionQuality.medium: 60,
        CompressionQuality.high: 85,
    }
    img_quality = quality_map[quality]

    # Compress images in PDF
    for page in writer.pages:
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            x_objects = page["/Resources"]["/XObject"].get_object()
            for obj_name in x_objects:
                obj = x_objects[obj_name].get_object()
                if obj.get("/Subtype") == "/Image":
                    try:
                        # Try to recompress image data
                        if obj.get("/Filter") in ["/DCTDecode", "/JPXDecode"]:
                            data = obj.get_data()
                            img = Image.open(io.BytesIO(data))
                            img_buffer = io.BytesIO()
                            img.save(img_buffer, format="JPEG", quality=img_quality, optimize=True)
                            obj.set_data(img_buffer.getvalue())
                    except Exception:
                        pass

    output = io.BytesIO()
    writer.write(output)
    result = output.getvalue()

    if add_watermark:
        result = _add_free_tier_watermark(result)

    return result


def parse_page_ranges(pages_str: str, total_pages: int) -> list[int]:
    """Parse page range string like '1-3,5,7-10' into list of page indices (0-based)."""
    pages = set()
    parts = pages_str.replace(" ", "").split(",")

    for part in parts:
        if "-" in part:
            start_end = part.split("-", 1)
            start = int(start_end[0])
            end = int(start_end[1])
            for i in range(max(1, start), min(total_pages, end) + 1):
                pages.add(i - 1)  # Convert to 0-based
        else:
            p = int(part)
            if 1 <= p <= total_pages:
                pages.add(p - 1)

    return sorted(pages)


def split_pdf(pdf_data: bytes, pages_str: str, add_watermark: bool = False) -> bytes:
    """Split PDF and return as ZIP archive."""
    reader = PdfReader(io.BytesIO(pdf_data))
    total_pages = len(reader.pages)

    # Parse page ranges into groups
    ranges = pages_str.replace(" ", "").split(",")
    groups = []
    for r in ranges:
        if "-" in r:
            start, end = r.split("-", 1)
            start_idx = max(0, int(start) - 1)
            end_idx = min(total_pages - 1, int(end) - 1)
            groups.append(list(range(start_idx, end_idx + 1)))
        else:
            p = int(r) - 1
            if 0 <= p < total_pages:
                groups.append([p])

    # Create ZIP with split PDFs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, page_indices in enumerate(groups, 1):
            writer = PdfWriter()
            for idx in page_indices:
                writer.add_page(reader.pages[idx])

            pdf_output = io.BytesIO()
            writer.write(pdf_output)
            pdf_bytes = pdf_output.getvalue()

            if add_watermark:
                pdf_bytes = _add_free_tier_watermark(pdf_bytes)

            if len(page_indices) == 1:
                filename = f"page_{page_indices[0]+1}.pdf"
            else:
                filename = f"pages_{page_indices[0]+1}-{page_indices[-1]+1}.pdf"
            zf.writestr(filename, pdf_bytes)

    return zip_buffer.getvalue()


def add_watermark(
    pdf_data: bytes,
    text: str,
    opacity: float = 0.3,
    position: WatermarkPosition = WatermarkPosition.diagonal,
    font_size: float = 48,
    color: tuple = (0.5, 0.5, 0.5),
    add_free_watermark: bool = False,
) -> bytes:
    """Add text watermark to all pages of a PDF."""
    reader = PdfReader(io.BytesIO(pdf_data))
    writer = PdfWriter()

    for page in reader.pages:
        media_box = page.mediabox
        page_width = float(media_box.width)
        page_height = float(media_box.height)

        # Create watermark overlay
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(Color(color[0], color[1], color[2], alpha=opacity))

        if position == WatermarkPosition.diagonal:
            c.saveState()
            c.translate(page_width / 2, page_height / 2)
            angle = math.degrees(math.atan2(page_height, page_width))
            c.rotate(angle)
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(-text_width / 2, -font_size / 2, text)
            c.restoreState()
        elif position == WatermarkPosition.center:
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(
                (page_width - text_width) / 2,
                (page_height - font_size) / 2,
                text,
            )
        elif position == WatermarkPosition.top_left:
            c.drawString(20, page_height - font_size - 20, text)
        elif position == WatermarkPosition.top_right:
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(page_width - text_width - 20, page_height - font_size - 20, text)
        elif position == WatermarkPosition.bottom_left:
            c.drawString(20, 20, text)
        elif position == WatermarkPosition.bottom_right:
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(page_width - text_width - 20, 20, text)

        c.save()
        packet.seek(0)

        watermark_reader = PdfReader(packet)
        page.merge_page(watermark_reader.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    result = output.getvalue()

    if add_free_watermark:
        result = _add_free_tier_watermark(result)

    return result


def protect_pdf(
    pdf_data: bytes,
    user_password: str,
    owner_password: Optional[str] = None,
    add_watermark_flag: bool = False,
) -> bytes:
    """Password-protect a PDF file."""
    if add_watermark_flag:
        pdf_data = _add_free_tier_watermark(pdf_data)

    reader = PdfReader(io.BytesIO(pdf_data))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Copy metadata
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        algorithm="AES-256",
    )

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
