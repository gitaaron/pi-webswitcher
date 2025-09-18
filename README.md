# Pi Web Switcher (Electron-free)

Loads multiple URLs from `config.yaml`, exposes `/show/<key>` API to switch which one is fullscreen, and runs on **Raspberry Pi 3A+** and **macOS**.

## Raspberry Pi Quickstart

```bash
./scripts/install_pi.sh
./scripts/run_pi.sh
```

If you prefer manual steps:
```bash
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebengine libqt5webengine5 libqt5webenginecore5 libqt5webenginewidgets5 python3-venv
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements-pi.txt
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
python app.py --config config.yaml --api-port 8080 --kiosk --no-mouse
```

> **Do not** `pip install PyQt5` on the Pi. Use the apt packages above.

## API
- `GET /keys`
- `GET /status`
- `GET /show/<key>`


### HTTP API (with curl examples)

#### From the same machine
curl http://localhost:8080/keys

#### From another device on your LAN (replace with your Pi's IP/host)
curl http://raspberrypi.local:8080/keys

## Dev/Diagnostics
- `--test-url URL` to bypass config
- `--remote-debug 9222` and open `http://localhost:9222`
- `--treat-secure "http://192.168.4.21:3000"` to simulate secure context
- `--clear-cache` to wipe Qt cache/service workers
- `--software-gl`, `--disable-gpu` (useful on mac only)
- `--bg-color white|#111111` (page background)

## Flutter (CanvasKit) tip
Serve with correct WASM MIME:
```bash
python serve_wasm.py build/web
```

## Autostart on Pi
Use `pi-webswitcher.service` in `/etc/systemd/system/` and:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pi-webswitcher
```
