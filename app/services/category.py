"""Бизнес-логика категорий каталога."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.categories = CategoryRepository(session)

    async def create(
        self,
        actor_id: int,
        app_id: str,
        data: CategoryCreate,
    ) -> Category:
        return await self.categories.create(
            app_id,
            data.model_dump(),
        )

    async def get_by_id(self, category_id: int, app_id: str) -> Category:
        category = await self.categories.get_by_id(category_id, app_id)
        if category is None:
            raise NotFoundError("Категория не найдена")
        return category

    async def list_for_tenant(self, app_id: str) -> list[Category]:
        return await self.categories.list_for_tenant(app_id)

    async def update(
        self,
        category_id: int,
        app_id: str,
        data: CategoryUpdate,
    ) -> Category:
        category = await self.categories.update(
            category_id,
            app_id,
            data.model_dump(exclude_unset=True),
        )
        if category is None:
            raise NotFoundError("Категория не найдена")
        return category
