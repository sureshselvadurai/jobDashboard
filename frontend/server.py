import os
import http.server
import socketserver

PORT = 5500
DIRECTORY = "."

class InjectingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.notifier_url = os.getenv("NOTIFIER_URL", "http://localhost:8500")
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        if self.path.endswith(".html"):
            self.send_header("Content-Type", "text/html")
        return super().end_headers()

    def send_head(self):
        if self.path == "/" or self.path.endswith("index.html"):
            path = self.translate_path("/index.html")  # ← this is the fix
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("__BACKEND_URL__", self.backend_url)
            content = content.replace("__NOTIFIER_URL__", self.notifier_url)
            encoded = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return None
        else:
            return super().send_head()


with socketserver.TCPServer(("0.0.0.0", PORT), InjectingHandler) as httpd:
    print(f"🌐 Serving frontend at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
