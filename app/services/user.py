"""Бизнес-логика пользовательского профиля и аватаров."""

import asyncio
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidFileError, NotFoundError
from app.db.models import User
from app.repositories.user import UserRepository


IMAGE_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


class UserService:
    def __init__(self, session: AsyncSession, static_dir: Path | None = None) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.static_dir = static_dir or Path("static")

    async def get_profile(self, user_id: int) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    async def update_profile(
        self,
        user_id: int,
        changes: dict[str, str | None],
    ) -> User:
        user = await self.get_profile(user_id)
        for field, value in changes.items():
            setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_avatar(
        self,
        user_id: int,
        contents: bytes,
        filename: str | None,
        content_type: str | None,
    ) -> User:
        user = await self.get_profile(user_id)
        mime_type = (content_type or "").lower()
        file_extension = Path(filename or "").suffix.lower()

        if mime_type in IMAGE_CONTENT_TYPES:
            extension = IMAGE_CONTENT_TYPES[mime_type]
        elif file_extension in IMAGE_EXTENSIONS:
            extension = file_extension
        else:
            raise InvalidFileError("Допускаются только файлы изображений")

        await asyncio.to_thread(self.static_dir.mkdir, parents=True, exist_ok=True)
        destination = self.static_dir / f"{uuid4().hex}{extension}"
        try:
            await asyncio.to_thread(destination.write_bytes, contents)
        except OSError:
            await asyncio.to_thread(destination.unlink, missing_ok=True)
            raise

        user.avatar_url = f"/static/{destination.name}"
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except SQLAlchemyError:
            await self.session.rollback()
            await asyncio.to_thread(destination.unlink, missing_ok=True)
            raise
        return user
