"""Асинхронное подключение к PostgreSQL и фабрика сессий."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


settings = get_settings()

# Соединение создается лениво: при импорте модуля запрос к БД не выполняется.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

# Для каждой операции создается отдельная асинхронная сессия.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Выдает сессию БД для FastAPI dependency и закрывает ее после запроса."""
    async with AsyncSessionLocal() as session:
        yield session
