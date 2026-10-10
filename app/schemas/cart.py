"""Pydantic-схемы корзины покупателя."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductResponse


class CartItemCreate(BaseModel):
    """Поля для добавления товара в корзину."""

    product_id: int
    quantity: int = Field(default=1, ge=1)
    selected_options: dict[str, Any] | None = None


class CartItemUpdate(BaseModel):
    """Новое количество товара в корзине."""

    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    """Представление позиции корзины вместе с товаром."""

    id: int
    app_id: str
    user_id: int
    product_id: int
    quantity: int
    selected_options: dict[str, Any] | None
    product: ProductResponse | None

    model_config = ConfigDict(from_attributes=True)


class CartSummaryResponse(BaseModel):
    """Корзина и итоговые значения для клиента."""

    items: list[CartItemResponse]
    total_items: int
    total_amount: float
