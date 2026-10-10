"""Зависимости аутентификации и RBAC для API v1."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_auth_service, get_current_user, security
from app.core.roles import UserRole
from app.db.models import User
from app.services.auth import AuthService


def require_role(
    allowed_roles: list[str],
) -> Callable[..., Awaitable[User]]:
    """Создает dependency для разрешенных ролей из access JWT."""
    try:
        normalized_roles = frozenset(UserRole(role.upper()) for role in allowed_roles)
    except (AttributeError, ValueError) as exc:
        raise ValueError("allowed_roles содержит неизвестную роль") from exc
    if not normalized_roles:
        raise ValueError("allowed_roles не может быть пустым")

    async def role_dependency(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        current_user: Annotated[User, Depends(get_current_user)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
    ) -> User:
        payload = auth_service.verify_token(
            credentials.credentials,
            "access",
        )
        try:
            token_role = UserRole(payload["role"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="В access token отсутствует допустимая роль",
            ) from exc

        if token_role != current_user.role or token_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return current_user

    return role_dependency
