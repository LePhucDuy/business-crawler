import time
import asyncio
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.api.response import APIResponse
import structlog

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter theo IP.
    Chỉ áp dụng cho các endpoint /api/ để tránh block health check.
    """

    def __init__(self, app):
        super().__init__(app)
        # {ip: deque([timestamp, ...])}
        self._requests: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        # Chỉ rate-limit các API endpoint
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.monotonic()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        max_requests = settings.RATE_LIMIT_REQUESTS

        async with self._lock:
            q = self._requests[client_ip]

            # Xóa các request cũ hơn cửa sổ thời gian
            while q and now - q[0] > window:
                q.popleft()

            if len(q) >= max_requests:
                oldest = q[0]
                retry_after = int(window - (now - oldest)) + 1
                logger.warning(
                    "rate_limit_exceeded",
                    client_ip=client_ip,
                    path=request.url.path,
                    count=len(q),
                    limit=max_requests,
                )
                response = APIResponse.fail(
                    message=f"Bạn đã vượt quá {max_requests} request/{window}s. Vui lòng thử lại sau {retry_after} giây.",
                    code=429,
                    detail={"retry_after_seconds": retry_after},
                )
                return JSONResponse(
                    status_code=429,
                    content=response.model_dump(mode="json"),
                    headers={"Retry-After": str(retry_after)},
                )

            q.append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max_requests - len(self._requests[client_ip]))
        response.headers["X-RateLimit-Window"] = str(window)
        return response

    def _get_client_ip(self, request: Request) -> str:
        # Hỗ trợ reverse proxy (nginx, traefik) qua header X-Forwarded-For
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
