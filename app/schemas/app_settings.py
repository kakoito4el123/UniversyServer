"""Pydantic-схемы настроек витрины приложения."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class AppSettingsUpdate(BaseModel):
    """Поля настроек, доступные для частичного обновления."""

    store_name: str | None = None
    currency: str | None = None
    delivery_fee: float | None = None
    min_order_amount: float | None = None
    is_active: bool | None = None
    extra_config: dict[str, Any] | None = None


class AppSettingsResponse(BaseModel):
    """Настройки витрины с дефолтами для еще не настроенного приложения."""

    id: int | None = None
    app_id: str
    store_name: str = "Мой Магазин"
    currency: str = "USD"
    delivery_fee: float = 0.0
    min_order_amount: float = 0.0
    is_active: bool = True
    extra_config: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
