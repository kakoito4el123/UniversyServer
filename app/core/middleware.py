"""Обратная совместимость для прежнего пути middleware."""

from app.core.middlewares import LoggingMiddleware

__all__ = ["LoggingMiddleware"]
