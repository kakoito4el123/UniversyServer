"""Контроллер пользовательского профиля."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import get_current_user, get_user_service
from app.db.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService


router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.get_profile(current_user.id)
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.update_profile(
        current_user.id,
        data.model_dump(exclude_unset=True),
    )
    return UserResponse.model_validate(user)


@router.post("/me/avatar", response_model=UserResponse)
async def upload_my_avatar(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.update_avatar(
        current_user.id,
        await file.read(),
        file.filename,
        file.content_type,
    )
    return UserResponse.model_validate(user)
