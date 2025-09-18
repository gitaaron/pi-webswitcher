from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import mimetypes, sys, os
mimetypes.add_type('application/wasm', '.wasm')
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
print(f"Serving {os.getcwd()} on http://0.0.0.0:8000")
ThreadingHTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler).serve_forever()
