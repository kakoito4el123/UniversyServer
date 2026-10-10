"""Асинхронный репозиторий категорий с изоляцией по app_id."""

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[Category]:
        return Category

    async def get_by_id(self, category_id: int, app_id: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(
                Category.id == category_id,
                Category.app_id == app_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_tenant(
        self,
        app_id: str,
        is_active_only: bool = True,
    ) -> list[Category]:
        statement = select(Category).where(Category.app_id == app_id)
        if is_active_only:
            statement = statement.where(Category.is_active.is_(True))
        statement = statement.order_by(Category.name, Category.id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, app_id: str, data: Mapping[str, object]) -> Category:
        category = Category(app_id=app_id, **dict(data))
        self.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(
        self,
        category_id: int,
        app_id: str,
        data: Mapping[str, object],
    ) -> Category | None:
        category = await self.get_by_id(category_id, app_id)
        if category is None:
            return None

        for field, value in data.items():
            if field in {"name", "slug", "parent_id", "image_url", "is_active"}:
                setattr(category, field, value)

        await self.session.commit()
        await self.session.refresh(category)
        return category
