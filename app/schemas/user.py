"""Pydantic-схемы для регистрации и ответа с данными пользователя."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    """Данные, необходимые для создания учетной записи."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def ensure_bcrypt_byte_limit(cls, value: str) -> str:
        """bcrypt ограничивает входные данные 72 байтами, а не символами."""
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Пароль не должен превышать 72 байта в UTF-8")
        return value


class UserResponse(BaseModel):
    """Безопасное представление пользователя без хеша пароля."""

    id: int
    username: str
    bio: str | None
    avatar_url: str | None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Необязательные поля для редактирования профиля."""

    bio: str | None = None
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    """Ответ с access JWT."""

    access_token: str
    token_type: str = "bearer"
