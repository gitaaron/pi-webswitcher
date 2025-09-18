#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv || true
source .venv/bin/activate
pip install -r requirements.txt
python app.py --test-url https://example.com --software-gl --disable-gpu --remote-debug 9222 --kiosk
