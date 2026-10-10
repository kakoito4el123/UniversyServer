"""Бизнес-логика товаров каталога."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.products = ProductRepository(session)

    async def create(
        self,
        actor_id: int,
        app_id: str,
        data: ProductCreate,
    ) -> Product:
        return await self.products.create(
            app_id,
            data.model_dump(),
        )

    async def get_by_id(self, product_id: int, app_id: str) -> Product:
        product = await self.products.get_by_id(product_id, app_id)
        if product is None:
            raise NotFoundError("Товар не найден")
        return product

    async def list_for_tenant(
        self,
        app_id: str,
        category_id: int | None = None,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        return await self.products.get_multi(
            app_id=app_id,
            category_id=category_id,
            search=search,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )

    async def update(
        self,
        product_id: int,
        app_id: str,
        data: ProductUpdate,
    ) -> Product:
        product = await self.products.update(
            product_id,
            app_id,
            data.model_dump(exclude_unset=True),
        )
        if product is None:
            raise NotFoundError("Товар не найден")
        return product

    async def soft_delete(self, product_id: int, app_id: str) -> None:
        deleted = await self.products.soft_delete(product_id, app_id)
        if not deleted:
            raise NotFoundError("Товар не найден")
