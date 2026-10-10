"""HTTP-контроллеры заметок."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_app_id, get_current_user, get_note_service
from app.db.models import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
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
async def get_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    search: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
) -> list[NoteResponse]:
    notes = await service.list_for_tenant(
        current_user.id,
        current_user.role,
        app_id,
        search,
        limit,
        offset,
    )
    return [NoteResponse.model_validate(note) for note in notes]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    note = await service.get_by_id(
        note_id,
        current_user.id,
        current_user.role,
        app_id,
    )
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    data: NoteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    note = await service.update(
        note_id,
        current_user.id,
        current_user.role,
        app_id,
        data.model_dump(exclude_unset=True),
    )
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[NoteService, Depends(get_note_service)],
) -> Response:
    await service.soft_delete(
        note_id,
        current_user.id,
        current_user.role,
        app_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
