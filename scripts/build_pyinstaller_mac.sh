#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate || { echo "Activate venv first"; exit 1; }
pip install pyinstaller
pyinstaller --name "Pi Web Switcher" --windowed --onefile app.py
echo "Built dist/Pi Web Switcher"
