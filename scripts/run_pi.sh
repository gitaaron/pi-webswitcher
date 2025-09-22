#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

# Force X11 session for Pi 5 compatibility
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}

# Additional Pi 5 compatibility flags
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox"

python app.py --config config.yaml --api-port 8080 --kiosk --no-mouse --software-gl --disable-gpu "$@"
