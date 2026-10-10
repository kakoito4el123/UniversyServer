"""Pydantic-схемы заказов."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    """Контактные и доставочные данные для создания заказа."""

    customer_name: str | None = None
    phone: str | None = None
    delivery_address: str | None = None
    comment: str | None = None


class OrderItemResponse(BaseModel):
    """Позиция заказа с сохраненными данными товара."""

    id: int
    product_id: int | None
    title_snapshot: str
    price_snapshot: float
    quantity: int
    selected_options: dict[str, Any] | None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Публичное представление заказа."""

    id: int
    app_id: str
    user_id: int
    total_amount: float
    status: str
    customer_name: str | None
    phone: str | None
    delivery_address: str | None
    comment: str | None
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Новое состояние заказа."""

    status: str
