"""Бизнес-логика заметок с изоляцией по пользователю и приложению."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.roles import UserRole
from app.db.models import Note
from app.repositories.note import NoteRepository


class NoteService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.notes = NoteRepository(session)

    async def create(
        self,
        actor_id: int,
        app_id: str,
        title: str,
        content: str | None,
    ) -> Note:
        return await self.notes.create(
            {
                "user_id": actor_id,
                "app_id": app_id,
                "title": title,
                "content": content,
            }
        )

    async def list_for_tenant(
        self,
        actor_id: int,
        role: UserRole,
        app_id: str,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[Note]:
        return await self.notes.get_multi(
            user_id=None if role == UserRole.ADMIN else actor_id,
            app_id=app_id,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_by_id(
        self,
        note_id: int,
        actor_id: int,
        role: UserRole,
        app_id: str,
    ) -> Note:
        note = await self.notes.get_by_id(
            note_id,
            user_id=None if role == UserRole.ADMIN else actor_id,
            app_id=app_id,
        )
        if note is None:
            raise NotFoundError("Заметка не найдена")
        return note

    async def update(
        self,
        note_id: int,
        actor_id: int,
        role: UserRole,
        app_id: str,
        update_data: dict[str, str | None],
    ) -> Note:
        note = await self.notes.update(
            note_id,
            user_id=None if role == UserRole.ADMIN else actor_id,
            update_data=update_data,
            app_id=app_id,
        )
        if note is None:
            raise NotFoundError("Заметка не найдена")
        return note

    async def soft_delete(
        self,
        note_id: int,
        actor_id: int,
        role: UserRole,
        app_id: str,
    ) -> None:
        deleted = await self.notes.soft_delete(
            note_id,
            user_id=None if role == UserRole.ADMIN else actor_id,
            app_id=app_id,
        )
        if not deleted:
            raise NotFoundError("Заметка не найдена")
