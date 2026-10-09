"""Middleware для журналирования HTTP-запросов."""

import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Логирует метод, путь, HTTP-статус и время обработки запроса."""

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

        start_time = perf_counter()
        status_code: int | None = None

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            duration_ms = (perf_counter() - start_time) * 1000
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "/")
            status: int | str = (
                status_code if status_code is not None else "no response"
            )
            logger.info(
                'HTTP %s %s | status=%s | duration=%.2f ms',
                method,
                path,
                status,
                duration_ms,
            )
