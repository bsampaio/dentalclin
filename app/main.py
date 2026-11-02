import logging
import mimetypes
import re
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .security import RateLimiter, client_ip

mimetypes.add_type("font/woff2", ".woff2")  # missing from the slim image's mime table
mimetypes.add_type("image/webp", ".webp")

log = logging.getLogger("uvicorn.error")
BASE = Path(__file__).parent
STATIC = BASE / "static"

if not config.WHATSAPP_NUMBER:
    log.warning("WHATSAPP_NUMBER not set: WhatsApp buttons will not work")

# Every call to action is WhatsApp. Pre-filled messages, one per context.
MESSAGES = {
    "agendar": "Olá! Gostaria de agendar uma avaliação para implante dentário.",
    "duvidas": "Olá! Tenho algumas dúvidas sobre implantes dentários.",
    "contato": "Olá! Gostaria de falar com a DentalClin.",
    "tratamento": "Olá! Gostaria de saber mais sobre os tratamentos da DentalClin.",
    "rodape": "Olá! Vim pelo site da DentalClin e gostaria de marcar uma consulta.",
}


def wa_url(text: str) -> str:
    return f"https://wa.me/{config.WHATSAPP_NUMBER}?text={quote(text)}"


def render_index() -> str:
    html = (BASE / "templates" / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"\{\{wa:(\w+)\}\}", lambda m: wa_url(MESSAGES[m.group(1)]), html)
    return html.replace("{{wa_base}}", f"https://wa.me/{config.WHATSAPP_NUMBER}")


INDEX_HTML = render_index()  # static page: rendered once at startup

limiter = RateLimiter(config.REQUESTS_PER_MIN, 60)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; "
        "font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; "
        "frame-ancestors 'none'; form-action 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Strict-Transport-Security": "max-age=15552000",
}
if not config.ALLOW_INDEXING:
    SECURITY_HEADERS["X-Robots-Tag"] = "noindex, nofollow"


@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.url.path == "/":  # only the HTML page is limited; static files are cheap and cached
        try:
            limiter.hit(client_ip(request))
        except Exception:  # HTTPException 429
            return JSONResponse({"detail": "rate_limited"}, status_code=429, headers=SECURITY_HEADERS)
    response = await call_next(request)
    response.headers.update(SECURITY_HEADERS)
    if request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=86400")
    return response


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)
