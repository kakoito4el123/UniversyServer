"""Асинхронный репозиторий товаров с изоляцией по app_id."""

from collections.abc import Mapping

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[Product]:
        return Product

    async def get_by_id(
        self,
        product_id: int,
        app_id: str,
        include_deleted: bool = False,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id,
            Product.app_id == app_id,
        )
        if not include_deleted:
            statement = statement.where(Product.is_deleted.is_(False))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        app_id: str,
        category_id: int | None = None,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Product]:
        statement = select(Product).where(
            Product.app_id == app_id,
            Product.is_deleted.is_(False),
        )
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Product.title.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )
        if min_price is not None:
            statement = statement.where(Product.price >= min_price)
        if max_price is not None:
            statement = statement.where(Product.price <= max_price)

        statement = (
            statement.order_by(Product.title, Product.id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, app_id: str, data: Mapping[str, object]) -> Product:
        product = Product(app_id=app_id, **dict(data))
        self.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(
        self,
        product_id: int,
        app_id: str,
        data: Mapping[str, object],
    ) -> Product | None:
        product = await self.get_by_id(product_id, app_id)
        if product is None:
            return None

        updateable_fields = {
            "category_id",
            "title",
            "description",
            "price",
            "unit",
            "stock",
            "attributes",
            "main_image_url",
            "is_available",
        }
        for field, value in data.items():
            if field in updateable_fields:
                setattr(product, field, value)

        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def soft_delete(self, product_id: int, app_id: str) -> bool:
        product = await self.get_by_id(product_id, app_id)
        if product is None:
            return False

        product.is_deleted = True
        await self.session.commit()
        return True
