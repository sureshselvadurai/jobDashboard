import http.server
import socketserver

PORT = 5500
DIRECTORY = "."

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

# Start HTTP server
with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving frontend at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
