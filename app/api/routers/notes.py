"""CRUD-маршруты заметок с изоляцией по пользователю и приложению."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_app_id, get_current_user
from app.db.database import get_db
from app.db.models import Note, User
from app.schemas.note import NoteCreate, NoteResponse


router = APIRouter()


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    app_id: str = Depends(get_app_id),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Создает заметку, связанную с текущим пользователем и приложением."""
    note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id,
        app_id=app_id,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return NoteResponse.model_validate(note)


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    current_user: User = Depends(get_current_user),
    app_id: str = Depends(get_app_id),
    db: AsyncSession = Depends(get_db),
) -> list[NoteResponse]:
    """Возвращает только заметки текущего пользователя в текущем приложении."""
    result = await db.execute(
        select(Note).where(
            Note.user_id == current_user.id,
            Note.app_id == app_id,
        )
    )
    notes = result.scalars().all()
    return [NoteResponse.model_validate(note) for note in notes]
