"""Точка сборки FastAPI-приложения."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers.auth import router as legacy_auth_router
from app.api.routers.notes import router as legacy_notes_router
from app.api.routers.users import router as legacy_users_router
from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.middlewares import LoggingMiddleware
from app.db.base_model import Base
from app.db.session import engine
from app.db.models import Note, User


settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Создает отсутствующие таблицы и освобождает пул при остановке."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="ServerUniversy API",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

register_exception_handlers(app)

app.include_router(api_v1_router, prefix="/api/v1")

# Сохраняем исходные URL на время миграции клиентов на /api/v1.
app.include_router(legacy_auth_router)
app.include_router(legacy_notes_router, prefix="/notes", tags=["notes"])
app.include_router(legacy_users_router, prefix="/users", tags=["users"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}