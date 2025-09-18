#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv --system-site-packages || true
source .venv/bin/activate
pip install -r requirements-pi.txt
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
python app.py --config config.yaml --api-port 8080 --kiosk --no-mouse
