import http.server
import socketserver
import urllib.request
import urllib.parse

PORT = 8080

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            url = self.path if self.path.startswith("http") else f"http://{self.headers['Host']}{self.path}"
            self.log_message("Fetching: %s", url)
            with urllib.request.urlopen(url) as response:
                self.send_response(response.getcode())
                for key, value in response.getheaders():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error fetching {self.path}: {e}")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        url = self.path if self.path.startswith("http") else f"http://{self.headers['Host']}{self.path}"
        req = urllib.request.Request(url, data=post_data, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())
                for key, value in response.getheaders():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error posting to {self.path}: {e}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"Proxy server running at http://localhost:{PORT}")
        httpd.serve_forever()
