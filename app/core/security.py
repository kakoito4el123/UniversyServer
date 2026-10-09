"""Хеширование паролей и выпуск JWT-токенов."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль алгоритмом bcrypt перед сохранением в БД."""
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает пароль с сохраненным bcrypt-хешем."""
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int) -> str:
    """Создает подписанный JWT с subject и временем истечения."""
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expires_at}
    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm="HS256",
    )
