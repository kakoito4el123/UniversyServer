"""Асинхронный репозиторий корзины с изоляцией по владельцу и app_id."""

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.db.models import CartItem, Product
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[CartItem]:
        return CartItem

    async def get_user_cart(self, user_id: int, app_id: str) -> list[CartItem]:
        result = await self.session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(
                CartItem.user_id == user_id,
                CartItem.app_id == app_id,
            )
            .order_by(CartItem.id)
        )
        return list(result.scalars().all())

    async def get_item(
        self,
        cart_item_id: int,
        user_id: int,
        app_id: str,
    ) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(
                CartItem.id == cart_item_id,
                CartItem.user_id == user_id,
                CartItem.app_id == app_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_or_update_item(
        self,
        user_id: int,
        app_id: str,
        product_id: int,
        quantity: int,
        selected_options: dict[str, Any] | None,
    ) -> CartItem:
        product_result = await self.session.execute(
            select(Product).where(
                Product.id == product_id,
                Product.app_id == app_id,
                Product.is_deleted.is_(False),
            )
        )
        product = product_result.scalar_one_or_none()
        if product is None:
            raise NotFoundError("Товар не найден")

        existing_items_result = await self.session.execute(
            select(CartItem)
            .where(
                CartItem.user_id == user_id,
                CartItem.app_id == app_id,
                CartItem.product_id == product_id,
            )
            .order_by(CartItem.id)
        )
        existing_item = next(
            (
                item
                for item in existing_items_result.scalars().all()
                if item.selected_options == selected_options
            ),
            None,
        )

        if existing_item is None:
            item = CartItem(
                user_id=user_id,
                app_id=app_id,
                product_id=product_id,
                quantity=quantity,
                selected_options=selected_options,
                product=product,
            )
            self.add(item)
        else:
            existing_item.quantity += quantity
            item = existing_item

        await self.session.flush()
        item_id = item.id
        await self.session.commit()
        refreshed_item = await self.get_item(item_id, user_id, app_id)
        if refreshed_item is None:
            raise RuntimeError("Добавленная позиция корзины не найдена")
        return refreshed_item

    async def update_quantity(
        self,
        cart_item_id: int,
        user_id: int,
        app_id: str,
        quantity: int,
    ) -> CartItem | None:
        item = await self.get_item(cart_item_id, user_id, app_id)
        if item is None:
            return None

        item.quantity = quantity
        await self.session.commit()
        return await self.get_item(cart_item_id, user_id, app_id)

    async def remove_item(
        self,
        cart_item_id: int,
        user_id: int,
        app_id: str,
    ) -> bool:
        item = await self.get_item(cart_item_id, user_id, app_id)
        if item is None:
            return False

        await self.session.delete(item)
        await self.session.commit()
        return True

    async def clear_cart(self, user_id: int, app_id: str) -> None:
        await self.session.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.app_id == app_id,
            )
        )
        await self.session.commit()
