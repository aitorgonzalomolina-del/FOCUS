"""
Servidor local para FOCUS Web
==============================
Abre el sitio en: http://localhost:8080

Uso:
    python server.py
    python server.py 3000   (puerto custom)
"""
import http.server
import socketserver
import webbrowser
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# Servir desde la carpeta FOCUS/ (padre de focus-web/) para que
# ../catalogo/ resuelva correctamente como /catalogo/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencia los logs

print(f"\n  FOCUS -- Servidor local activo")
print(f"  http://localhost:{PORT}/focus-web/")
print(f"  Ctrl+C para detener\n")

webbrowser.open(f"http://localhost:{PORT}/focus-web/index.html")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
