"""ASGI middleware приложения."""

import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Записывает method, path, HTTP status и время обработки каждого запроса."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = perf_counter()
        status_code: int | None = None

        async def capture_response_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture_response_status)
        finally:
            logger.info(
                "HTTP %s %s | status=%s | duration=%.2f ms",
                scope.get("method", "UNKNOWN"),
                scope.get("path", "/"),
                status_code if status_code is not None else "no response",
                (perf_counter() - started_at) * 1000,
            )
