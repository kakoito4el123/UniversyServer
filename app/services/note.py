"""Бизнес-логика заметок с изоляцией по пользователю и приложению."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.repositories.note import NoteRepository


class NoteService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.notes = NoteRepository(session)

    async def create(
        self,
        user_id: int,
        app_id: str,
        title: str,
        content: str,
    ) -> Note:
        note = self.notes.add(
            Note(
                user_id=user_id,
                app_id=app_id,
                title=title,
                content=content,
            )
        )
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def list_for_tenant(self, user_id: int, app_id: str) -> list[Note]:
        return await self.notes.list_for_tenant(user_id, app_id)
