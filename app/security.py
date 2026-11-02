"""Per-client rate limiting. State lives in memory only (reset on restart); IPs are never logged."""
import threading
import time
from collections import deque

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    """The real client address.

    The container is only reachable through Tailscale Serve/Funnel on this host, which appends the
    connecting address to X-Forwarded-For. Use the right-most entry: anything to its left came
    from the client and can be forged.
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Sliding window: at most `limit` events per `window` seconds per key."""

    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> deque[float]:
        q = self._events.setdefault(key, deque())
        while q and q[0] <= now - self.window:
            q.popleft()
        return q

    def check(self, key: str) -> None:
        """Raise 429 if the key is over its limit, without recording an event."""
        now = time.monotonic()
        with self._lock:
            q = self._recent(key, now)
            if len(q) >= self.limit:
                retry = int(q[0] + self.window - now) + 1
                raise HTTPException(429, "rate_limited", headers={"Retry-After": str(retry)})

    def record(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._recent(key, now).append(now)
            if len(self._events) > 10_000:  # drop idle keys so memory stays bounded
                for k in [k for k, q in self._events.items() if not q or q[-1] <= now - self.window]:
                    del self._events[k]

    def hit(self, key: str) -> None:
        """Check, then record: the usual "N requests per window" limit."""
        self.check(key)
        self.record(key)
