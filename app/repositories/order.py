"""Асинхронный репозиторий заказов с tenant-фильтрацией."""

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[Order]:
        return Order

    async def create_order(
        self,
        app_id: str,
        user_id: int,
        total_amount: float,
        details: Mapping[str, Any],
        items_data: Sequence[Mapping[str, Any]],
    ) -> Order:
        order = Order(
            app_id=app_id,
            user_id=user_id,
            total_amount=total_amount,
            customer_name=details.get("customer_name"),
            phone=details.get("phone"),
            delivery_address=details.get("delivery_address"),
            comment=details.get("comment"),
            items=[
                OrderItem(
                    product_id=item.get("product_id"),
                    title_snapshot=item["title_snapshot"],
                    price_snapshot=item["price_snapshot"],
                    quantity=item.get("quantity", 1),
                    selected_options=item.get("selected_options"),
                )
                for item in items_data
            ],
        )
        self.add(order)
        await self.session.flush()
        order_id = order.id
        await self.session.commit()

        created_order = await self.get_by_id(order_id, app_id)
        if created_order is None:
            raise RuntimeError("Созданный заказ не найден")
        return created_order

    async def get_by_id(
        self,
        order_id: int,
        app_id: str,
        user_id: int | None = None,
    ) -> Order | None:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.id == order_id,
                Order.app_id == app_id,
            )
        )
        if user_id is not None:
            statement = statement.where(Order.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_user_orders(self, user_id: int, app_id: str) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.user_id == user_id,
                Order.app_id == app_id,
            )
            .order_by(Order.created_at.desc(), Order.id.desc())
        )
        return list(result.scalars().all())

    async def list_all_orders_for_tenant(
        self,
        app_id: str,
        status: str | None = None,
    ) -> list[Order]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.app_id == app_id)
        )
        if status is not None:
            statement = statement.where(Order.status == status)
        statement = statement.order_by(Order.created_at.desc(), Order.id.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update_status(
        self,
        order_id: int,
        app_id: str,
        status: str,
    ) -> Order | None:
        order = await self.get_by_id(order_id, app_id)
        if order is None:
            return None

        order.status = status
        await self.session.commit()
        return await self.get_by_id(order_id, app_id)
