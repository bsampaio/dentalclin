import os


def _flag(name: str, default: str) -> bool:
    return os.environ.get(name, default) == "1"


# Public business WhatsApp number, digits only with country code (e.g. 5511999999999). Set in .env.
WHATSAPP_NUMBER = "".join(c for c in os.environ.get("WHATSAPP_NUMBER", "") if c.isdigit())

# Study project: keep search engines out until the clinic approves going live (set ALLOW_INDEXING=1).
ALLOW_INDEXING = _flag("ALLOW_INDEXING", "0")

REQUESTS_PER_MIN = int(os.environ.get("REQUESTS_PER_MIN", "120"))
