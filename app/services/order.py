"""Бизнес-логика заказов с ограничением доступа по tenant и владельцу."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.core.roles import UserRole
from app.db.models import Order, User
from app.repositories.cart import CartRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse
from app.services.cart import CartService


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.cart = CartService(session)
        self.cart_repository = CartRepository(session)

    async def create_order_from_cart(
        self,
        user_id: int,
        app_id: str,
        data: OrderCreate,
    ) -> OrderResponse:
        cart_items = await self.cart_repository.get_user_cart(user_id, app_id)
        if not cart_items:
            raise BadRequestError("Корзина пуста")

        items_data: list[dict[str, object]] = []
        total_amount = 0.0
        for cart_item in cart_items:
            product = cart_item.product
            if (
                product is None
                or product.app_id != app_id
                or product.is_deleted
                or not product.is_available
            ):
                raise BadRequestError(
                    "Один или несколько товаров в корзине недоступны"
                )

            price = product.price
            total_amount += price * cart_item.quantity
            items_data.append(
                {
                    "product_id": product.id,
                    "title_snapshot": product.title,
                    "price_snapshot": price,
                    "quantity": cart_item.quantity,
                    "selected_options": cart_item.selected_options,
                }
            )

        order: Order = await self.orders.create_order(
            app_id=app_id,
            user_id=user_id,
            total_amount=total_amount,
            details=data.model_dump(),
            items_data=items_data,
        )
        await self.cart.clear_cart(user_id, app_id)
        return OrderResponse.model_validate(order)

    async def get_order(
        self,
        order_id: int,
        app_id: str,
        current_user: User,
    ) -> OrderResponse:
        order = await self.orders.get_by_id(
            order_id,
            app_id,
            user_id=(
                None
                if current_user.role == UserRole.ADMIN
                else current_user.id
            ),
        )
        if order is None:
            raise NotFoundError("Заказ не найден")
        if (
            current_user.role != UserRole.ADMIN
            and order.user_id != current_user.id
        ):
            raise ForbiddenError("Нет доступа к этому заказу")
        return OrderResponse.model_validate(order)

    async def list_my_orders(
        self,
        user_id: int,
        app_id: str,
    ) -> list[OrderResponse]:
        orders = await self.orders.list_user_orders(user_id, app_id)
        return [OrderResponse.model_validate(order) for order in orders]

    async def list_all_orders(
        self,
        app_id: str,
        status: str | None = None,
    ) -> list[OrderResponse]:
        orders = await self.orders.list_all_orders_for_tenant(app_id, status)
        return [OrderResponse.model_validate(order) for order in orders]

    async def update_status(
        self,
        order_id: int,
        app_id: str,
        status: str,
    ) -> OrderResponse:
        order = await self.orders.update_status(order_id, app_id, status)
        if order is None:
            raise NotFoundError("Заказ не найден")
        return OrderResponse.model_validate(order)

    async def pay_order_with_balance(
        self,
        order_id: int,
        app_id: str,
        current_user: User,
    ) -> OrderResponse:
        order_result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id, Order.app_id == app_id)
            .with_for_update()
        )
        order = order_result.scalar_one_or_none()
        if order is None:
            raise NotFoundError("Заказ не найден")

        if (
            order.user_id != current_user.id
            and current_user.role != UserRole.ADMIN
        ):
            raise ForbiddenError("Нет доступа к этому заказу")

        if order.status != "NEW":
            raise BadRequestError("Заказ уже оплачен или отменен")

        user_result = await self.session.execute(
            select(User)
            .where(User.id == current_user.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        payer = user_result.scalar_one_or_none()
        if payer is None:
            raise NotFoundError("Пользователь не найден")

        if payer.balance < order.total_amount:
            raise BadRequestError("Недостаточно средств на балансе")

        payer.balance -= order.total_amount
        order.status = "PAID"
        await self.session.commit()
        await self.session.refresh(order)
        return OrderResponse.model_validate(order)
