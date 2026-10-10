"""Исключения предметной области и обработчики HTTP-ответов."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


class AppException(Exception):
    """Базовая ошибка приложения с ожидаемым HTTP-статусом."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UnauthorizedError(AppException):
    def __init__(
        self,
        message: str = "Требуется действительная авторизация",
    ) -> None:
        super().__init__(message, 401)


class NotFoundError(AppException):
    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message, 404)


class ConflictError(AppException):
    def __init__(self, message: str = "Конфликт данных") -> None:
        super().__init__(message, 409)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Недостаточно прав") -> None:
        super().__init__(message, 403)


class InvalidFileError(AppException):
    def __init__(self, message: str = "Недопустимый файл") -> None:
        super().__init__(message, 415)


async def app_exception_handler(
    _: Request,
    exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message},
        headers={"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None,
    )


async def http_exception_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail: Any = exc.detail
    if not isinstance(detail, str):
        detail = "Некорректный запрос"
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": detail},
        headers=exc.headers,
    )


async def validation_exception_handler(
    _: Request,
    __: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Некорректные данные запроса"},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Внутренняя ошибка сервера"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует стандартные и предметные обработчики исключений."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
