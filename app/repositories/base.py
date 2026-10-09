"""Общие асинхронные операции репозиториев SQLAlchemy."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_model import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(ABC, Generic[ModelT]):
    """Базовый репозиторий для чтения и добавления ORM-сущностей."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @property
    @abstractmethod
    def model(self) -> type[ModelT]:
        """ORM-модель, которой управляет конкретный репозиторий."""
        raise NotImplementedError

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        return entity
