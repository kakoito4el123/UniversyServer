"""Асинхронный SQLAlchemy engine и фабрика сессий."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Создает async engine с пулом, подходящим для выбранного диалекта."""
    engine_options: dict[str, object] = {
        "echo": settings.debug,
        "pool_pre_ping": True,
    }
    if settings.database_url.startswith("postgresql+asyncpg://"):
        engine_options.update(pool_size=10, max_overflow=20)
    return create_async_engine(settings.database_url, **engine_options)


settings = get_settings()
engine = create_database_engine(settings)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Выдает асинхронную сессию на запрос и гарантированно закрывает ее."""
    async with AsyncSessionLocal() as session:
        yield session
