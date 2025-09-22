#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

# Pi 5 specific compatibility settings
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}

# Enhanced Chromium flags for Pi 5
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox --disable-software-rasterizer --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding"

# Memory and performance optimizations for Pi 5
export MALLOC_ARENA_MAX=2
export MALLOC_MMAP_THRESHOLD_=131072
export MALLOC_TRIM_THRESHOLD_=131072
export MALLOC_TOP_PAD_=131072
export MALLOC_MMAP_MAX_=65536

echo "Starting Pi Web Switcher on Pi 5 with compatibility mode..."
python app.py --config config.yaml --api-port 8080 --kiosk --no-mouse --software-gl --disable-gpu --clear-cache "$@"
