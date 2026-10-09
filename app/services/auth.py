"""Бизнес-логика регистрации, входа и проверки access-токенов."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import InvalidTokenError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, username: str, password: str) -> User:
        if await self.users.get_by_username(username) is not None:
            raise ConflictError("Пользователь с таким логином уже существует")

        user = self.users.add(
            User(username=username, hashed_password=hash_password(password))
        )
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError(
                "Пользователь с таким логином уже существует"
            ) from exc
        return user

    async def login(self, username: str, password: str) -> str:
        user = await self.users.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Неверный логин или пароль")
        return create_access_token(user.id)

    async def get_user_from_token(self, token: str) -> User:
        try:
            payload = decode_access_token(token)
            subject = payload.get("sub")
            user_id = int(subject)
        except (InvalidTokenError, ValueError, TypeError, KeyError) as exc:
            raise UnauthorizedError() from exc

        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError()
        return user
