"""Pydantic-схемы заметок."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteCreate(BaseModel):
    """Поля, передаваемые при создании заметки."""

    title: str = Field(min_length=1, max_length=255)
    content: str | None = None


class NoteUpdate(BaseModel):
    """Изменяемые поля заметки."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None

    @field_validator("title")
    @classmethod
    def title_cannot_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Заголовок не может быть null")
        return value


class NoteResponse(BaseModel):
    """Публичное представление сохраненной заметки."""

    id: int
    title: str
    content: str | None
    user_id: int
    app_id: str
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
