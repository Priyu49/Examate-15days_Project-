"""Small ASGI request metrics without logging request or response contents."""

import json
import logging
import math
import time

logger = logging.getLogger("mitramaati.requests")


class RequestMetricsMiddleware:
    """Log request duration and approximate payload token counts."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()
        request_bytes = 0
        response_bytes = 0
        status_code = 500

        async def measured_receive():
            nonlocal request_bytes
            message = await receive()
            if message["type"] == "http.request":
                request_bytes += len(message.get("body", b""))
            return message

        async def measured_send(message):
            nonlocal response_bytes, status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                response_bytes += len(message.get("body", b""))
            await send(message)

        try:
            await self.app(scope, measured_receive, measured_send)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            input_tokens = math.ceil(request_bytes / 4)
            output_tokens = math.ceil(response_bytes / 4)
            logger.info(
                "request_metrics %s",
                json.dumps({
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": status_code,
                    "latency_ms": round(elapsed_ms, 2),
                    "input_tokens_estimate": input_tokens,
                    "output_tokens_estimate": output_tokens,
                    "total_tokens_estimate": input_tokens + output_tokens,
                }),
            )
