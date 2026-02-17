"""EditPDFree API - PDF Processing Made Simple."""

import os
import io
import stripe
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

from models import (
    HtmlToPdfRequest,
    UrlToPdfRequest,
    CompressionQuality,
    WatermarkPosition,
    UsageResponse,
    PLAN_LIMITS,
)
from database import init_db, get_usage_count, generate_api_key, hash_key
from auth import APIKeyMiddleware
from rate_limiter import RateLimitMiddleware, get_reset_date
from pdf_engine import (
    html_to_pdf,
    url_to_pdf,
    merge_pdfs,
    compress_pdf,
    split_pdf,
    add_watermark,
    protect_pdf,
    close_browser,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    yield
    await close_browser()


app = FastAPI(
    title="EditPDFree API",
    description="PDF Processing API - Convert, merge, compress, split, watermark and protect PDFs.",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware order matters: auth first, then rate limiting
app.add_middleware(RateLimitMiddleware)
app.add_middleware(APIKeyMiddleware)

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ─── Landing Page ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "EditPDFree API"}


# ─── PDF Conversion Endpoints ──────────────────────────────────────────────────

@app.post("/api/v1/html-to-pdf")
async def api_html_to_pdf(request: Request, body: HtmlToPdfRequest):
    """Convert HTML to PDF."""
    try:
        should_watermark = request.state.plan_config.get("watermark", False)
        pdf_bytes = await html_to_pdf(body.html, body.options, add_watermark=should_watermark)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="output.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/v1/url-to-pdf")
async def api_url_to_pdf(request: Request, body: UrlToPdfRequest):
    """Convert URL to PDF."""
    # Basic URL validation
    if not body.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        should_watermark = request.state.plan_config.get("watermark", False)
        pdf_bytes = await url_to_pdf(body.url, body.options, add_watermark=should_watermark)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="output.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/v1/merge")
async def api_merge_pdfs(request: Request, files: list[UploadFile] = File(...)):
    """Merge multiple PDF files into one."""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDF files required")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files allowed")

    try:
        pdf_files = []
        for f in files:
            content = await f.read()
            if not content[:5] == b"%PDF-":
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{f.filename}' is not a valid PDF",
                )
            pdf_files.append(content)

        should_watermark = request.state.plan_config.get("watermark", False)
        result = merge_pdfs(pdf_files, add_watermark=should_watermark)

        return Response(
            content=result,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="merged.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")


@app.post("/api/v1/compress")
async def api_compress_pdf(
    request: Request,
    file: UploadFile = File(...),
    quality: CompressionQuality = Form(CompressionQuality.medium),
):
    """Compress a PDF file."""
    try:
        content = await file.read()
        if not content[:5] == b"%PDF-":
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

        should_watermark = request.state.plan_config.get("watermark", False)
        result = compress_pdf(content, quality, add_watermark=should_watermark)

        original_size = len(content)
        compressed_size = len(result)
        reduction = round((1 - compressed_size / original_size) * 100, 1) if original_size > 0 else 0

        return Response(
            content=result,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="compressed.pdf"',
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
                "X-Compression-Ratio": f"{reduction}%",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")


@app.post("/api/v1/split")
async def api_split_pdf(
    request: Request,
    file: UploadFile = File(...),
    pages: str = Form(..., description="Page ranges, e.g. '1-3,5,7-10'"),
):
    """Split a PDF into multiple files."""
    try:
        content = await file.read()
        if not content[:5] == b"%PDF-":
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

        should_watermark = request.state.plan_config.get("watermark", False)
        result = split_pdf(content, pages, add_watermark=should_watermark)

        return Response(
            content=result,
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="split_pages.zip"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Split failed: {str(e)}")


@app.post("/api/v1/watermark")
async def api_add_watermark(
    request: Request,
    file: UploadFile = File(...),
    text: str = Form(..., min_length=1, max_length=200),
    opacity: float = Form(0.3, ge=0.0, le=1.0),
    position: WatermarkPosition = Form(WatermarkPosition.diagonal),
    font_size: float = Form(48, ge=8, le=200),
):
    """Add text watermark to all pages of a PDF."""
    try:
        content = await file.read()
        if not content[:5] == b"%PDF-":
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

        should_watermark = request.state.plan_config.get("watermark", False)
        result = add_watermark(
            content,
            text=text,
            opacity=opacity,
            position=position,
            font_size=font_size,
            add_free_watermark=should_watermark,
        )

        return Response(
            content=result,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="watermarked.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watermark failed: {str(e)}")


@app.post("/api/v1/protect")
async def api_protect_pdf(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(..., min_length=1, max_length=128),
    owner_password: str = Form(None, max_length=128),
):
    """Password-protect a PDF file."""
    try:
        content = await file.read()
        if not content[:5] == b"%PDF-":
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

        should_watermark = request.state.plan_config.get("watermark", False)
        result = protect_pdf(
            content,
            user_password=password,
            owner_password=owner_password,
            add_watermark_flag=should_watermark,
        )

        return Response(
            content=result,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="protected.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protection failed: {str(e)}")


# ─── Usage & Key Management ────────────────────────────────────────────────────

@app.get("/api/v1/usage", response_model=UsageResponse)
async def api_get_usage(request: Request):
    """Check API usage for current month."""
    plan = request.state.plan
    key_hash = request.state.key_hash
    client_ip = request.client.host if request.client else "unknown"

    used = await get_usage_count(key_hash, client_ip)
    plan_config = PLAN_LIMITS[plan]
    limit = plan_config["monthly_limit"]

    return UsageResponse(
        used=used,
        remaining=max(0, limit - used),
        plan=plan,
        monthly_limit=limit,
        reset_date=get_reset_date(),
    )


@app.post("/api/v1/generate-key")
async def api_generate_key(
    plan: str = Query(default="free", regex="^(free|starter|pro|business)$"),
    email: str = Query(default=None),
):
    """Generate a new API key. In production, this should be behind admin auth."""
    key = await generate_api_key(plan=plan, email=email)
    return {
        "api_key": key,
        "plan": plan,
        "monthly_limit": PLAN_LIMITS[plan]["monthly_limit"],
        "message": "Save this key securely. It cannot be retrieved again.",
    }


# ─── Stripe Webhook ──────────────────────────────────────────────────────────────

STRIPE_PRICE_TO_PLAN = {
    "price_1T1gglJW4PGBAbQ7Ftp5pcxA": "starter",
    "price_1T1ggvJW4PGBAbQ7BqWrSsiX": "pro",
    "price_1T1ggwJW4PGBAbQ7B1JyhAW1": "business",
}

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")

        # Get the price ID from line items
        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
        if line_items and line_items.data:
            price_id = line_items.data[0].price.id
            plan = STRIPE_PRICE_TO_PLAN.get(price_id, "starter")

            # Generate API key for the customer
            api_key = await generate_api_key(plan=plan, email=customer_email)

            # TODO: Send email with API key (for now, logged)
            print(f"[STRIPE] New {plan} subscription: {customer_email} -> key prefix: {api_key[:12]}...")

    return {"status": "ok"}


# ─── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "production") != "production",
    )
