import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request, status
from .config import get_settings


class RateLimiter:
    def __init__(self) -> None:
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request) -> None:
        settings = get_settings()
        now = time.time()
        key = request.client.host if request.client else "unknown"
        bucket = self.hits[key]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        bucket.append(now)


rate_limiter = RateLimiter()
