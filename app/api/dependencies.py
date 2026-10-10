"""Dependency injection для сервисов API и аутентифицированного пользователя."""

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.db.models import User
from app.services.auth import AuthService
from app.services.category import CategoryService
from app.services.note import NoteService
from app.services.product import ProductService
from app.services.user import UserService


security = HTTPBearer(auto_error=False)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_note_service(db: AsyncSession = Depends(get_db)) -> NoteService:
    return NoteService(db)


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


async def get_app_id(
    x_app_id: str = Header(..., alias="X-App-ID", description="ID приложения"),
) -> str:
    """Получает tenant id из обязательного заголовка клиентского приложения."""
    return x_app_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Проверяет JWT через сервис и возвращает существующего пользователя."""
    if credentials is None:
        raise UnauthorizedError()
    return await auth_service.get_user_from_token(credentials.credentials)
