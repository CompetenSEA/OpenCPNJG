import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

# Minimal valid MVT tile with one empty layer named 'layer'
TILE_BYTES = bytes.fromhex("1a0c0a056c617965722880207802")

data_store = {}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data_store[(0, 0, 0)] = body
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parts = self.path.lstrip("/").split("/")
        if len(parts) == 3:
            z, x, y_ext = parts
            y = y_ext.split(".")[0]
            key = (int(z), int(x), int(y))
            tile = data_store.get(key)
            if tile:
                self.send_response(200)
                self.send_header("Content-Type", "application/x-protobuf")
                self.end_headers()
                self.wfile.write(tile)
                return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *args, **kwargs):  # pragma: no cover
        pass


def test_tileserver_stub():
    server = HTTPServer(("localhost", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        req = urllib.request.Request(
            f"http://localhost:{port}/ingest", data=TILE_BYTES, method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
        with urllib.request.urlopen(f"http://localhost:{port}/0/0/0.mvt") as resp:
            assert resp.status == 200
            content = resp.read()
        assert len(content) > 0
        assert content.startswith(b"\x1a")
    finally:
        server.shutdown()
        thread.join()
