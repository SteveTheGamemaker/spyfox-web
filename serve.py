#!/usr/bin/env python3
"""Serve the browser game locally, including HTTP byte ranges for large resources."""
import argparse
import re
import shutil
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      '.wasm': 'application/wasm', '.so': 'application/wasm'}

    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        if not path.is_file():
            return super().send_head()
        stream = path.open('rb')
        size = path.stat().st_size
        start, end = 0, size - 1
        range_header = self.headers.get('Range')
        if range_header:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
            if match and any(match.groups()):
                first, last = match.groups()
                if first:
                    start = int(first)
                    end = min(int(last), size - 1) if last else size - 1
                else:
                    start = max(0, size - int(last))
            if not match or not any(match.groups()) or start > end or start >= size:
                stream.close()
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
        self.send_response(206 if range_header else 200)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        if range_header:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream.seek(start)
        self.remaining = end - start + 1
        return stream

    def copyfile(self, source, outputfile):
        try:
            if self.remaining is None:
                shutil.copyfileobj(source, outputfile)
            else:
                while self.remaining > 0:
                    block = source.read(min(1024 * 1024, self.remaining))
                    if not block:
                        break
                    outputfile.write(block)
                    self.remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8088)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent / 'web'
    server = ThreadingHTTPServer((args.host, args.port), partial(Handler, directory=str(root)))
    print(f'Spy Fox: http://{args.host}:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
