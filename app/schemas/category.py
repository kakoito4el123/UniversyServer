"""Pydantic-схемы категорий каталога."""

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Поля для создания категории."""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    parent_id: int | None = None
    image_url: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """Необязательные поля для частичного обновления категории."""

    name: str | None = None
    slug: str | None = None
    parent_id: int | None = None
    image_url: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    """Публичное представление категории."""

    id: int
    app_id: str
    name: str
    slug: str
    parent_id: int | None
    image_url: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
