"""Маршруты для чтения и редактирования профиля пользователя."""

import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter()
STATIC_DIR = Path("static")
IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Возвращает профиль аутентифицированного пользователя."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Обновляет только переданные поля профиля."""
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/me/avatar", response_model=UserResponse)
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Сохраняет аватар изображения и обновляет URL в профиле пользователя."""
    content_type = (file.content_type or "").lower()
    filename_extension = Path(file.filename or "").suffix.lower()

    if content_type in IMAGE_CONTENT_TYPES:
        extension = IMAGE_CONTENT_TYPES[content_type]
    elif filename_extension in IMAGE_EXTENSIONS:
        extension = filename_extension
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Допускаются только файлы изображений",
        )

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    destination = STATIC_DIR / filename
    file_handle = await asyncio.to_thread(destination.open, "wb")
    upload_complete = False

    try:
        while chunk := await file.read(1024 * 1024):
            await asyncio.to_thread(file_handle.write, chunk)
        upload_complete = True
    finally:
        try:
            await asyncio.to_thread(file_handle.close)
        finally:
            if not upload_complete:
                await asyncio.to_thread(destination.unlink, missing_ok=True)

    current_user.avatar_url = f"/static/{filename}"
    database_updated = False
    try:
        try:
            await db.commit()
            await db.refresh(current_user)
        except SQLAlchemyError:
            await db.rollback()
            raise
        database_updated = True
    finally:
        if not database_updated:
            await asyncio.to_thread(destination.unlink, missing_ok=True)

    return UserResponse.model_validate(current_user)
