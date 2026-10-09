"""Репозиторий заметок с tenant-фильтрацией."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[Note]:
        return Note

    async def list_for_tenant(self, user_id: int, app_id: str) -> list[Note]:
        result = await self.session.execute(
            select(Note).where(Note.user_id == user_id, Note.app_id == app_id)
        )
        return list(result.scalars().all())
