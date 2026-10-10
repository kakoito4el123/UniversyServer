"""Бизнес-логика корзины покупателя."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import CartItem
from app.repositories.cart import CartRepository
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartSummaryResponse,
)


class CartService:
    def __init__(self, session: AsyncSession) -> None:
        self.cart = CartRepository(session)

    async def get_user_cart(
        self,
        user_id: int,
        app_id: str,
    ) -> CartSummaryResponse:
        items = await self.cart.get_user_cart(user_id, app_id)
        total_items = sum(item.quantity for item in items)
        total_amount = sum(
            item.product.price * item.quantity
            for item in items
            if item.product is not None
        )
        return CartSummaryResponse(
            items=items,
            total_items=total_items,
            total_amount=total_amount,
        )

    async def add_to_cart(
        self,
        user_id: int,
        app_id: str,
        data: CartItemCreate,
    ) -> CartItem:
        return await self.cart.add_or_update_item(
            user_id=user_id,
            app_id=app_id,
            product_id=data.product_id,
            quantity=data.quantity,
            selected_options=data.selected_options,
        )

    async def update_item(
        self,
        cart_item_id: int,
        user_id: int,
        app_id: str,
        data: CartItemUpdate,
    ) -> CartItem:
        item = await self.cart.update_quantity(
            cart_item_id,
            user_id,
            app_id,
            data.quantity,
        )
        if item is None:
            raise NotFoundError("Позиция корзины не найдена")
        return item

    async def remove_item(
        self,
        cart_item_id: int,
        user_id: int,
        app_id: str,
    ) -> None:
        removed = await self.cart.remove_item(cart_item_id, user_id, app_id)
        if not removed:
            raise NotFoundError("Позиция корзины не найдена")

    async def clear_cart(self, user_id: int, app_id: str) -> None:
        await self.cart.clear_cart(user_id, app_id)
