# EditPDFree API

PDF Processing API built with FastAPI. Convert HTML/URL to PDF, merge, compress, split, watermark and password-protect PDFs.

## Quick Start

### Docker (recommended)

```bash
docker-compose up -d
```

API available at `http://localhost:8000`

### Manual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
playwright install chromium
python main.py
```

### Ubuntu Server (Oracle Cloud)

```bash
chmod +x setup.sh
sudo ./setup.sh
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/html-to-pdf` | Convert HTML to PDF |
| POST | `/api/v1/url-to-pdf` | Convert URL to PDF |
| POST | `/api/v1/merge` | Merge multiple PDFs |
| POST | `/api/v1/compress` | Compress PDF |
| POST | `/api/v1/split` | Split PDF into parts |
| POST | `/api/v1/watermark` | Add text watermark |
| POST | `/api/v1/protect` | Password-protect PDF |
| GET | `/api/v1/usage` | Check API usage |

## Authentication

Pass API key via `X-API-Key` header. No key = free tier (50/month, watermarked).

```bash
# Generate a key
curl -X POST "http://localhost:8000/api/v1/generate-key?plan=starter&email=you@mail.com"
```

## Plans

| Plan | Price | Monthly Limit | Watermark |
|------|-------|---------------|-----------|
| Free | $0 | 50 | Yes |
| Starter | $9/mo | 500 | No |
| Pro | $24/mo | 5,000 | No |
| Business | $49/mo | 20,000 | No |

## Example

```bash
curl -X POST http://localhost:8000/api/v1/html-to-pdf \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello</h1>"}' \
  -o output.pdf
```

## Swagger Docs

Visit `http://localhost:8000/docs` for interactive API documentation.
