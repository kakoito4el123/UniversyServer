"""Бизнес-логика регистрации, входа и проверки access-токенов."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.config import get_settings
from app.core.roles import UserRole
from app.db.models import RefreshToken, User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository


class AuthService:
    ACCESS_TOKEN_TTL = timedelta(minutes=15)
    REFRESH_TOKEN_TTL = timedelta(days=7)
    JWT_ALGORITHM = "HS256"
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens_repository = RefreshTokenRepository(session)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.password_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        return cls.password_context.verify(password, password_hash)

    @staticmethod
    def _encode_token(
        subject: str | int,
        token_type: str,
        expires_in: timedelta,
        role: UserRole | str | None = None,
    ) -> str:
        settings = get_settings()
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": str(subject),
            "type": token_type,
            "iat": now,
            "exp": now + expires_in,
            "jti": uuid4().hex,
        }
        if token_type == "access" and role is not None:
            payload["role"] = role.value if isinstance(role, UserRole) else role
        return jwt.encode(
            payload,
            settings.secret_key.get_secret_value(),
            algorithm=AuthService.JWT_ALGORITHM,
        )

    @classmethod
    def create_access_token(
        cls,
        subject: str | int,
        role: UserRole | str = UserRole.USER,
    ) -> str:
        return cls._encode_token(
            subject,
            "access",
            cls.ACCESS_TOKEN_TTL,
            role,
        )

    @classmethod
    def create_refresh_token(cls, subject: str | int) -> str:
        return cls._encode_token(subject, "refresh", cls.REFRESH_TOKEN_TTL)

    @staticmethod
    def verify_token(token: str, expected_type: str) -> dict[str, Any]:
        """Проверяет JWT-подпись, срок действия и тип токена."""
        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                settings.secret_key.get_secret_value(),
                algorithms=[AuthService.JWT_ALGORITHM],
            )
        except InvalidTokenError as exc:
            raise UnauthorizedError(
                "Недействительный или просроченный токен"
            ) from exc

        if payload.get("type") != expected_type:
            raise UnauthorizedError("Неверный тип токена")
        return payload

    def _add_refresh_session(
        self,
        subject: str | int,
        role: UserRole | str,
    ) -> tuple[str, str]:
        access_token = self.create_access_token(subject, role)
        refresh_token = self.create_refresh_token(subject)
        payload = self.verify_token(refresh_token, "refresh")
        refresh_jti = payload.get("jti")
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if not isinstance(refresh_jti, str):
            raise RuntimeError("Сформированный refresh JWT не содержит jti")

        self.refresh_tokens_repository.add(
            RefreshToken(
                jti=refresh_jti,
                user_id=int(subject),
                expires_at=expires_at,
            )
        )
        return access_token, refresh_token

    async def issue_token_pair(
        self,
        subject: str | int,
        role: UserRole | str = UserRole.USER,
    ) -> tuple[str, str]:
        token_pair = self._add_refresh_session(subject, role)
        await self.session.commit()
        return token_pair

    async def register(self, username: str, password: str) -> User:
        if await self.users.get_by_username(username) is not None:
            raise ConflictError("Пользователь с таким логином уже существует")

        user = self.users.add(
            User(
                username=username,
                hashed_password=self.hash_password(password),
            )
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

    async def login(self, username: str, password: str) -> tuple[str, str]:
        user = await self.users.get_by_username(username)
        if user is None or not self.verify_password(password, user.hashed_password):
            raise UnauthorizedError("Неверный логин или пароль")
        return await self.issue_token_pair(user.id, user.role)

    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        payload = self.verify_token(refresh_token, "refresh")
        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise UnauthorizedError("Некорректный refresh token") from exc

        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Пользователь не найден")

        refresh_jti = payload.get("jti")
        if not isinstance(refresh_jti, str):
            raise UnauthorizedError("Некорректный refresh token")

        now = datetime.now(timezone.utc)
        if not await self.refresh_tokens_repository.consume(
            refresh_jti,
            user.id,
            now,
        ):
            await self.session.rollback()
            raise UnauthorizedError("Refresh token уже использован или отозван")

        try:
            token_pair = self._add_refresh_session(user.id, user.role)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return token_pair

    async def revoke_refresh_token(self, token: str | None) -> None:
        """Отзывает refresh JWT, если он действителен и еще не использован."""
        if not token:
            return
        try:
            payload = self.verify_token(token, "refresh")
            user_id = int(payload["sub"])
            jti = payload["jti"]
        except (UnauthorizedError, KeyError, TypeError, ValueError):
            return

        if not isinstance(jti, str):
            return
        await self.refresh_tokens_repository.consume(
            jti,
            user_id,
            datetime.now(timezone.utc),
        )
        await self.session.commit()

    async def get_user_from_token(self, token: str) -> User:
        try:
            payload = self.verify_token(token, "access")
            subject = payload.get("sub")
            user_id = int(subject)
        except (ValueError, TypeError, KeyError) as exc:
            raise UnauthorizedError() from exc

        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError()
        return user
