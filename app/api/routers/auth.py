"""Маршруты регистрации и входа."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse


logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Создает нового пользователя и возвращает только публичные поля."""
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        )

    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as exc:
        await db.rollback()
        logger.info("Конфликт при регистрации пользователя %s", user_data.username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        ) from exc

    return UserResponse.model_validate(user)


@router.post("/login")
async def login(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Проверяет учетные данные и возвращает access JWT."""
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
