"""Pydantic-схемы товаров каталога."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Поля для создания товара."""

    title: str = Field(min_length=1, max_length=255)
    category_id: int | None = None
    description: str | None = None
    price: float = Field(default=0.0, ge=0.0)
    unit: str = "шт"
    stock: int | None = Field(default=None, ge=0)
    attributes: dict[str, Any] | None = None
    main_image_url: str | None = None
    is_available: bool = True


class ProductUpdate(BaseModel):
    """Необязательные поля для частичного обновления товара."""

    title: str | None = None
    category_id: int | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0.0)
    unit: str | None = None
    stock: int | None = Field(default=None, ge=0)
    attributes: dict[str, Any] | None = None
    main_image_url: str | None = None
    is_available: bool | None = None


class ProductResponse(BaseModel):
    """Публичное представление товара."""

    id: int
    app_id: str
    category_id: int | None
    title: str
    description: str | None
    price: float
    unit: str
    stock: int | None
    attributes: dict[str, Any] | None
    main_image_url: str | None
    is_available: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
