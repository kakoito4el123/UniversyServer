"""Асинхронный репозиторий заметок с учетом владельца и tenant-а."""

from collections.abc import Mapping

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[Note]:
        return Note

    async def create(self, data: Mapping[str, object]) -> Note:
        note = Note(**dict(data))
        self.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_by_id(
        self,
        note_id: int,
        user_id: int | None,
        app_id: str | None = None,
    ) -> Note | None:
        statement = select(Note).where(
            Note.id == note_id,
            Note.is_deleted.is_(False),
        )
        if user_id is not None:
            statement = statement.where(Note.user_id == user_id)
        if app_id is not None:
            statement = statement.where(Note.app_id == app_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        user_id: int | None,
        app_id: str,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[Note]:
        statement = select(Note).where(
            Note.app_id == app_id,
            Note.is_deleted.is_(False),
        )
        if user_id is not None:
            statement = statement.where(Note.user_id == user_id)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(Note.title.ilike(pattern), Note.content.ilike(pattern))
            )
        statement = statement.order_by(Note.created_at.desc(), Note.id.desc())
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(
        self,
        note_id: int,
        user_id: int | None,
        update_data: Mapping[str, object],
        app_id: str | None = None,
    ) -> Note | None:
        note = await self.get_by_id(note_id, user_id, app_id)
        if note is None:
            return None
        for field, value in update_data.items():
            if field in {"title", "content"}:
                setattr(note, field, value)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def soft_delete(
        self,
        note_id: int,
        user_id: int | None,
        app_id: str | None = None,
    ) -> bool:
        note = await self.get_by_id(note_id, user_id, app_id)
        if note is None:
            return False
        note.is_deleted = True
        await self.session.commit()
        return True
