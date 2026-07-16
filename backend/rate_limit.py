from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    """Simple per-IP limiter for a single backend instance."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.lock = Lock()

    def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = monotonic()
        with self.lock:
            attempts = self.requests[client_ip]
            while attempts and attempts[0] <= now - self.window_seconds:
                attempts.popleft()
            if len(attempts) >= self.limit:
                raise HTTPException(429, "Trop de tentatives. Réessayez plus tard.")
            attempts.append(now)


login_rate_limit = InMemoryRateLimiter(5, 60)
register_rate_limit = InMemoryRateLimiter(10, 3600)
