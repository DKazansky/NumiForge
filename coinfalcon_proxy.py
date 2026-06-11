#!/usr/bin/env python3
"""
CoinFalcon Local Proxy Server v1.1
- Serves CoinFalcon HTML files directly (no separate http.server needed)
- Proxies Greysheet and PCGS API calls with CORS headers

Setup (one-time):
    pip install flask requests

Run:
    python coinfalcon_proxy.py

Then open in browser:
    http://localhost:3001/coinfalcon_dev.html
    http://localhost:3001/coinfalcon_demo.html

Press Ctrl+C to stop.
"""

from flask import Flask, request, Response, send_from_directory
import requests, os, sys

app = Flask(__name__)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TARGETS = {
    'greysheet': 'https://cpgpublicapiv2.greysheet.com',
    'pcgs':      'https://api.pcgs.com',
}

CORS = {
    'Access-Control-Allow-Origin':          '*',
    'Access-Control-Allow-Headers':         'Authorization, Content-Type, Numista-API-Key, x-api-key, x-api-token',
    'Access-Control-Allow-Methods':         'GET, POST, OPTIONS',
    'Access-Control-Allow-Private-Network': 'true',
}


# ── Static file serving ────────────────────────────────────────────────────
@app.route('/')
def index():
    # List available CoinFalcon files
    files = [f for f in os.listdir(BASE_DIR) if f.startswith('coinfalcon') and f.endswith('.html')]
    links = ''.join(f'<li><a href="/{f}">{f}</a></li>' for f in sorted(files))
    return f'''<!DOCTYPE html><html><head><title>CoinFalcon Proxy</title>
    <style>body{{font-family:monospace;background:#0e0e0e;color:#e2e0da;padding:40px}}
    a{{color:#c9a84c}}li{{margin:8px 0}}</style></head>
    <body><h2 style="color:#c9a84c">CoinFalcon Proxy v1.1</h2>
    <p style="color:#4caf7d">&#10003; Running on port {PORT}</p>
    <h3>Available files:</h3><ul>{links}</ul>
    <p style="color:#666;font-size:12px">Proxying: {", ".join(TARGETS.keys())}</p>
    </body></html>'''

@app.route('/<path:filename>')
def serve_file(filename):
    # Route API proxy paths
    prefix = filename.split('/')[0]
    if prefix in TARGETS:
        return proxy_request(prefix, '/'.join(filename.split('/')[1:]))
    # Serve static files from the same folder as this script
    try:
        return send_from_directory(BASE_DIR, filename)
    except Exception:
        return Response(f'File not found: {filename}', 404)


# ── API proxy ──────────────────────────────────────────────────────────────
def proxy_request(prefix, path):
    if request.method == 'OPTIONS':
        return Response('', 200, headers=CORS)

    base = TARGETS[prefix]
    url  = f'{base}/{path}'
    hdrs = {k: v for k, v in request.headers
            if k.lower() not in ('host', 'content-length', 'transfer-encoding')}
    try:
        resp = requests.request(
            method  = request.method,
            url     = url,
            headers = hdrs,
            params  = request.args,
            json    = request.get_json(silent=True),
            timeout = 20,
        )
        out = Response(resp.content, status=resp.status_code,
                       content_type=resp.headers.get('Content-Type', 'application/json'))
        for k, v in CORS.items():
            out.headers[k] = v
        return out
    except requests.exceptions.ConnectionError as e:
        return Response(f'{{"error":"Connection failed: {e}"}}', 502,
                        headers=CORS, content_type='application/json')
    except requests.exceptions.Timeout:
        return Response('{"error":"Request timed out"}', 504,
                        headers=CORS, content_type='application/json')
    except Exception as e:
        return Response(f'{{"error":"{e}"}}', 500,
                        headers=CORS, content_type='application/json')


# ── Health check ───────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return {'status': 'ok', 'proxies': list(TARGETS.keys()), 'port': PORT}


@app.after_request
def add_cors(response):
    for k, v in CORS.items():
        response.headers[k] = v
    return response


if __name__ == '__main__':
    files = [f for f in os.listdir(BASE_DIR) if f.startswith('coinfalcon') and f.endswith('.html')]
    print(f'\nCoinFalcon Proxy Server v1.1')
    print(f'Running on http://localhost:{PORT}')
    print(f'\nOpen in browser:')
    for f in sorted(files):
        print(f'  http://localhost:{PORT}/{f}')
    print(f'\nProxying: {", ".join(TARGETS.keys())}')
    print(f'Press Ctrl+C to stop.\n')
    app.run(host='0.0.0.0', port=PORT, debug=False)
