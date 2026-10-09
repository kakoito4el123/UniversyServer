"""Точка входа FastAPI: приложение, middleware и обработчики ошибок."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.middleware import LoggingMiddleware
from app.api.routers.notes import router as notes_router
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.db.base_model import Base
from app.db.database import engine


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Создает таблицы при запуске и освобождает пул при остановке."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="ServerUniversy API",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Разрешает запросы от любых доменов. Cookie-аутентификация не включена:
# браузеры не разрешают credentials вместе с allow_origins=["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(notes_router, prefix="/notes", tags=["notes"])
app.include_router(users_router, prefix="/users", tags=["users"])


@app.exception_handler(HTTPException)
async def http_exception_handler(
    _: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Возвращает HTTP-ошибки в общем формате, сохраняя их статус-код."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    __: RequestValidationError,
) -> JSONResponse:
    """Возвращает ошибки входных данных без раскрытия лишних деталей."""
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Некорректные данные запроса",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Логирует непредвиденную ошибку и отвечает безопасным JSON."""
    logger.error(
        "Необработанная ошибка при запросе %s",
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Внутренняя ошибка сервера",
        },
    )


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Проверка доступности процесса API; состояние БД здесь не проверяется."""
    return {"status": "ok"}