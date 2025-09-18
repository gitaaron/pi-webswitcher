#!/usr/bin/env bash
set -euo pipefail
echo "[1/4] Updating apt…"
sudo apt update
echo "[2/4] Installing Qt + PyQt (system)…"
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebengine libqt5webengine5 libqt5webenginecore5 libqt5webenginewidgets5 python3-venv
echo "[3/4] Creating venv with system packages…"
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
echo "[4/4] Installing Python deps (pip)…"
pip install -r requirements-pi.txt
echo "✔ Done. To run: ./scripts/run_pi.sh"
