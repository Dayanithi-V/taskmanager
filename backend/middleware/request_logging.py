import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("smart_task_manager.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status code, and elapsed milliseconds per request."""

    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            client_host = request.client.host if request.client else "-"
            logger.info(
                "%s %s %s %.2fms",
                client_host,
                request.method,
                request.url.path,
                elapsed_ms,
                extra={
                    "http.method": request.method,
                    "http.path": request.url.path,
                    "http.status_code": status_code,
                    "duration_ms": round(elapsed_ms, 2),
                },
            )
