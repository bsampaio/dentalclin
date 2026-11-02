"""End-to-end check of the running site (stdlib only).  Usage: python tests/check_site.py http://127.0.0.1:8087"""
import re
import sys
import urllib.error
import urllib.request

base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8087").rstrip("/")
fails = []


def get(path):
    try:
        r = urllib.request.urlopen(base + path, timeout=10)
        return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), ""


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        fails.append(name)


status, headers, html = get("/")
h = {k.lower(): v for k, v in headers.items()}
check("GET / is 200", status == 200, status)
check("healthz ok", get("/healthz")[0] == 200)
check("CSP present and strict", "script-src 'self'" in h.get("content-security-policy", "") and "unsafe" not in h.get("content-security-policy", ""))
for name in ("x-content-type-options", "x-frame-options", "referrer-policy", "strict-transport-security", "permissions-policy"):
    check(f"header {name}", name in h)
check("no server banner", "server" not in h, h.get("server"))
check("no mailto links", "mailto:" not in html.lower())
links = re.findall(r'href="(https://wa\.me/[^"]*)"', html)
check("has WhatsApp links", len(links) >= 8, len(links))
check("every wa.me link has the number", all(re.match(r"https://wa\.me/\d{12,13}(\?|$)", l) for l in links))
check("no unrendered template tokens", "{{" not in html)
check("no inline scripts or styles", not re.search(r"<script(?![^>]*src)", html) and "<style" not in html and ' style="' not in html)
check("exactly one h1", html.count("<h1") == 1)
for path in ("/static/style.css", "/static/app.js", "/static/fonts/geist-latin.woff2", "/static/img/logo.webp", "/static/img/pilares-600.webp", "/static/img/camburi-1600.webp"):
    check(f"asset {path}", get(path)[0] == 200)
check("docs disabled", get("/docs")[0] == 404 and get("/openapi.json")[0] == 404)
check("no path traversal", get("/static/..%2f..%2fetc%2fpasswd")[0] in (400, 404))
print("\nRESULT:", "all passed" if not fails else f"{len(fails)} failed: {fails}")
sys.exit(1 if fails else 0)
