"""Контроллеры регистрации и входа."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_service
from app.schemas.user import TokenResponse, UserCreate, UserResponse
from app.services.auth import AuthService


router = APIRouter(tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await service.register(data.username, data.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    token = await service.login(data.username, data.password)
    return TokenResponse(access_token=token)
