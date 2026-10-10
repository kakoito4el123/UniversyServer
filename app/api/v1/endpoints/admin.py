"""Административные HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service
from app.api.v1.dependencies import require_role
from app.core.roles import UserRole
from app.db.models import User
from app.schemas.user import UserResponse
from app.services.user import UserService


router = APIRouter(tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    _: Annotated[User, Depends(require_role([UserRole.ADMIN.value]))],
    service: Annotated[UserService, Depends(get_user_service)],
) -> list[UserResponse]:
    users = await service.list_users()
    return [UserResponse.model_validate(user) for user in users]
