"""Общие зависимости API для определения приложения и пользователя."""

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import User


security = HTTPBearer()


async def get_app_id(
    x_app_id: str = Header(..., alias="X-App-ID", description="ID приложения"),
) -> str:
    """Требует идентификатор клиентского приложения в заголовке."""
    return x_app_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Проверяет JWT и загружает его пользователя из базы данных."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный или отсутствующий токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key.get_secret_value(),
            algorithms=["HS256"],
        )
        subject = payload.get("sub")
        user_id = int(subject)
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise unauthorized from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise unauthorized

    return user
