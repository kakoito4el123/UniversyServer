"""Корневой router версии API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.notes import router as notes_router
from app.api.v1.users import router as users_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(notes_router, prefix="/notes")
router.include_router(users_router, prefix="/users")
