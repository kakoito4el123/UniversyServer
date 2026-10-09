"""Контроллер заметок."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_app_id, get_current_user, get_note_service
from app.db.models import User
from app.schemas.note import NoteCreate, NoteResponse
from app.services.note import NoteService


router = APIRouter(tags=["notes"])


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    note = await service.create(
        current_user.id,
        app_id,
        data.title,
        data.content,
    )
    return NoteResponse.model_validate(note)


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
) -> list[NoteResponse]:
    notes = await service.list_for_tenant(current_user.id, app_id)
    return [NoteResponse.model_validate(note) for note in notes]
