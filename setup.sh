#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# EditPDFree API - Ubuntu Setup Script
# Tested on Ubuntu 22.04 / 24.04 (Oracle Cloud free tier)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

echo "=== EditPDFree API Setup ==="

# ── 1. System updates ──────────────────────────────────────────────────────
echo "[1/6] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# ── 2. Install Python 3.12+ ───────────────────────────────────────────────
echo "[2/6] Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv

# ── 3. Install system deps for Playwright/Chromium ─────────────────────────
echo "[3/6] Installing Chromium dependencies..."
sudo apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 libxshmfence1 \
    fonts-liberation fonts-noto-color-emoji

# ── 4. Set up project ─────────────────────────────────────────────────────
echo "[4/6] Setting up Python environment..."
APP_DIR="${APP_DIR:-/opt/editpdfree-api}"
sudo mkdir -p "$APP_DIR"
sudo chown "$USER:$USER" "$APP_DIR"

cd "$APP_DIR"

# Copy files if running from source
if [ -f "$(dirname "$0")/main.py" ]; then
    cp -r "$(dirname "$0")"/* "$APP_DIR/"
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ── 5. Install Playwright browsers ────────────────────────────────────────
echo "[5/6] Installing Playwright Chromium..."
playwright install chromium
playwright install-deps chromium

# ── 6. Create systemd service ─────────────────────────────────────────────
echo "[6/6] Creating systemd service..."
sudo tee /etc/systemd/system/editpdfree-api.service > /dev/null <<EOF
[Unit]
Description=EditPDFree PDF API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin
Environment=PDF_API_DB=$APP_DIR/data/pdf_api.db
Environment=PORT=8000
Environment=ENV=production
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create data directory
mkdir -p "$APP_DIR/data"

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable editpdfree-api
sudo systemctl start editpdfree-api

echo ""
echo "=== Setup complete! ==="
echo "API running at http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status editpdfree-api   # Check status"
echo "  sudo systemctl restart editpdfree-api   # Restart"
echo "  sudo journalctl -u editpdfree-api -f    # View logs"
echo ""
echo "Generate an API key:"
echo "  curl -X POST 'http://localhost:8000/api/v1/generate-key?plan=free'"
