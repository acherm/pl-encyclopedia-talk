#!/usr/bin/env python3
"""Petit serveur HTTP avec support des requêtes Range (nécessaire pour les vidéos).

Usage :  python3 serve.py [port]     (défaut : 8000)
"""
import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler + Content-Range, pour que les vidéos se lisent et se rembobinent."""

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass  # le client a coupé la connexion : normal, on ignore

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if not m:
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        size = os.fstat(f.fileno()).st_size
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            f.close()
            self.send_error(416, "Requested Range Not Satisfiable")
            return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f.seek(start)
        self._range_remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "_range_remaining", None)
        if remaining is None:
            try:
                super().copyfile(source, outputfile)
            except BrokenPipeError:
                pass  # le client a coupé (seek vidéo, changement de slide) : normal
            return
        self._range_remaining = None
        try:
            while remaining > 0:
                buf = source.read(min(64 * 1024, remaining))
                if not buf:
                    break
                outputfile.write(buf)
                remaining -= len(buf)
        except BrokenPipeError:
            pass

    def log_message(self, fmt, *args):
        pass  # silence


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = partial(RangeHandler, directory=os.path.dirname(os.path.abspath(__file__)))
    print(f"Slides: http://localhost:{port}")
    ThreadingHTTPServer(("", port), handler).serve_forever()
