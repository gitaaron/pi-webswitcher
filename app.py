#!/usr/bin/env python3
"""
Pi Web Switcher — lightweight, kiosk switcher for Raspberry Pi and macOS.

Features:
- Loads multiple URLs from config.yaml, first entry shows on startup.
- API: GET /keys, /status, /show/<key> to switch visible page.
- Preloads all pages; switching is instant (no reload).
- Dev/diagnostic flags: --treat-secure, --software-gl, --disable-gpu, --remote-debug, --clear-cache, --test-url
- Background color control: --bg-color (default: white).

On Raspberry Pi: install PyQt5 + QtWebEngine via apt; use requirements-pi.txt for pip deps.
"""
import argparse, os, shutil, signal, sys, threading, yaml
from typing import Dict
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from flask import Flask, jsonify
from flask_cors import CORS
from waitress import serve as waitress_serve

class SwitchBus(QtCore.QObject):
    switchRequested = pyqtSignal(str)

def start_api_server(switch_bus: SwitchBus, routes: Dict[str, str], host: str, port: int):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    @app.get("/")
    def root():
        return jsonify({"endpoints": ["/show/<key>", "/status", "/keys"], "keys": list(routes.keys())})

    @app.get("/keys")
    def keys():
        return jsonify(list(routes.keys()))

    @app.get("/status")
    def status():
        return jsonify({"active": _AppState.active_key, "keys": list(routes.keys())})

    @app.get("/show/<key>")
    def show(key: str):
        if key not in routes:
            return jsonify({"error": f"unknown key '{key}'", "keys": list(routes.keys())}), 404
        switch_bus.switchRequested.emit(key)
        return jsonify({"ok": True, "showing": key})

    # Convenience alias to support `GET /<key>` fast switching
    @app.get("/<key>")
    def show_alias(key: str):
        if key in ("keys", "status", "show"):
            # avoid shadowing existing endpoints
            return jsonify({"error": "reserved path"}), 404
        return show(key)

    def _runner():
        # Increase threads to handle bursts and reduce latency under concurrent calls
        waitress_serve(app, host=host, port=port, threads=8)
    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    return t

class QuietPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        noisy = [
            "Service Worker API unavailable",
            "The current context is NOT secure",
            "Unrecognized feature: 'identity-credentials-get'",
        ]
        if any(s in message for s in noisy):
            return
        try:
            lvl = ["Info", "Warning", "Error"][int(level)]
        except Exception:
            lvl = str(level)
        sys.stderr.write(f"js[{lvl}]: {message} ({sourceID}:{lineNumber})\n")

BG_COLOR = "white"

class WebPane(QWebEngineView):
    def __init__(self, url: str, user_agent_suffix: str = "", cache_dir: str = ""):
        super().__init__()
        profile = QWebEngineProfile.defaultProfile()
        if cache_dir:
            profile.setCachePath(cache_dir)
            profile.setPersistentStoragePath(cache_dir)
            # Prefer disk cache for persistence; increase capacity for heavy apps
            try:
                profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
                # ~256 MB; adjust if running on very constrained devices
                profile.setHttpCacheMaximumSize(256 * 1024 * 1024)
            except Exception:
                pass
        try:
            # Keep cookies and storage across sessions to leverage app-level caching
            profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        except Exception:
            pass
        if user_agent_suffix:
            ua = profile.httpUserAgent() + " " + user_agent_suffix
            profile.setHttpUserAgent(ua)
        self.setPage(QuietPage(self))
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setUrl(QtCore.QUrl(url))
        self.page().setBackgroundColor(QtGui.QColor(BG_COLOR))
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.settings().setAttribute(self.settings().JavascriptEnabled, True)
        self.settings().setAttribute(self.settings().PluginsEnabled, False)
        self.settings().setAttribute(self.settings().FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(lambda r: r.accept())

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, routes: Dict[str, str], start_key: str, kiosk: bool, show_mouse: bool):
        super().__init__()
        self.routes = routes
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.key_to_index = {}
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "pi-webswitcher")
        os.makedirs(cache_dir, exist_ok=True)
        for i, (key, url) in enumerate(routes.items()):
            view = WebPane(url, user_agent_suffix="PiWebSwitcher/1.0", cache_dir=cache_dir)
            self.stack.addWidget(view)
            self.key_to_index[key] = i
        self.switch_to(start_key)
        if kiosk:
            self.kioskize(mouse=show_mouse)
        QShortcut = QtWidgets.QShortcut
        esc = QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self); esc.activated.connect(self.close)
        quit_short = QShortcut(QtGui.QKeySequence("Ctrl+Q"), self); quit_short.activated.connect(self.close)
        quit_short2 = QShortcut(QtGui.QKeySequence("Meta+Q"), self); quit_short2.activated.connect(self.close)

    def kioskize(self, mouse: bool):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        if not mouse:
            self.setCursor(Qt.BlankCursor)

    def switch_to(self, key: str):
        if key not in self.key_to_index:
            return
        self.stack.setCurrentIndex(self.key_to_index[key])
        _AppState.active_key = key

class _AppState:
    active_key: str = ""

def parse_args():
    p = argparse.ArgumentParser(description="Pi Web Switcher (PyQt + QtWebEngine)")
    p.add_argument("--config", default="config.yaml", help="Path to YAML mapping keys->urls")
    p.add_argument("--api-host", default="0.0.0.0", help="API bind host")
    p.add_argument("--api-port", type=int, default=8080, help="API bind port")
    p.add_argument("--kiosk", action="store_true", help="Start fullscreen kiosk")
    p.add_argument("--no-mouse", action="store_true", help="Hide mouse cursor in kiosk mode")
    p.add_argument("--treat-secure", default="", help="Comma-separated HTTP origins to treat as secure (DEV ONLY)")
    p.add_argument("--software-gl", action="store_true", help="Force software OpenGL (fix black screens)")
    p.add_argument("--disable-gpu", action="store_true", help="Disable GPU compositing in Chromium")
    p.add_argument("--remote-debug", type=int, default=0, help="Enable remote devtools at this port")
    p.add_argument("--clear-cache", action="store_true", help="Clear cache dir before start")
    p.add_argument("--test-url", default="", help="Load only this URL (ignore config) for diagnostics")
    p.add_argument("--bg-color", default="white", help="Page background color (e.g., white, black, #RRGGBB)")
    return p.parse_args()

def load_routes(path: str) -> Dict[str, str]:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict) or not data:
        raise SystemExit(f"No routes found in {path}. Add key: url pairs.")
    return data

def _append_flag(env_key: str, addition: str):
    existing = os.environ.get(env_key, "")
    os.environ[env_key] = (existing + " " + addition).strip()

def _apply_dev_secure_origins(origins_csv: str):
    if not origins_csv.strip(): return
    origins = ",".join([o.strip() for o in origins_csv.split(",") if o.strip()])
    if not origins: return
    user_dir = os.path.join(os.path.expanduser("~"), ".cache", "pi-webswitcher", "chromium-dev")
    os.makedirs(user_dir, exist_ok=True)
    _append_flag("QTWEBENGINE_CHROMIUM_FLAGS",
        f'--unsafely-treat-insecure-origin-as-secure={origins} --user-data-dir="{user_dir}"'
    )

def _apply_remote_debug(port: int):
    if port > 0:
        _append_flag("QTWEBENGINE_CHROMIUM_FLAGS", f"--remote-debugging-port={port}")

def _apply_disable_gpu(disable: bool):
    if disable:
        _append_flag("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu --disable-gpu-compositing")

def _apply_software_gl(enable: bool):
    if enable:
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

def main():
    args = parse_args()
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "pi-webswitcher")
    if args.clear_cache and os.path.isdir(cache_dir):
        shutil.rmtree(cache_dir, ignore_errors=True)
    _apply_dev_secure_origins(args.treat_secure)
    _apply_remote_debug(args.remote_debug)
    _apply_disable_gpu(args.disable_gpu)
    _apply_software_gl(args.software_gl)
    routes = {"test": args.test_url} if args.test_url else load_routes(args.config)
    first_key = next(iter(routes.keys())); _AppState.active_key = first_key
    global BG_COLOR; BG_COLOR = args.bg_color
    app = QApplication(sys.argv)
    app.setApplicationName("Pi Web Switcher"); app.setOrganizationName("PiWeb")
    app.setQuitOnLastWindowClosed(True)
    win = MainWindow(routes, start_key=first_key, kiosk=args.kiosk, show_mouse=not args.no_mouse)
    win.show() if not args.kiosk else None
    switch_bus = SwitchBus(); switch_bus.switchRequested.connect(win.switch_to, Qt.QueuedConnection)
    start_api_server(switch_bus, routes, args.api_host, args.api_port)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
