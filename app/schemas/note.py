"""Pydantic-схемы заметок."""

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """Поля, передаваемые при создании заметки."""

    title: str = Field(min_length=1, max_length=255)
    content: str


class NoteResponse(BaseModel):
    """Публичное представление сохраненной заметки."""

    id: int
    title: str
    content: str
    user_id: int
    app_id: str

    model_config = ConfigDict(from_attributes=True)
