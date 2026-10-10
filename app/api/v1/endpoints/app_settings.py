"""HTTP-контроллер настроек витрины."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_id, get_app_settings_service
from app.api.v1.dependencies import require_role
from app.core.roles import UserRole
from app.db.models import User
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdate
from app.services.app_settings import AppSettingsService


router = APIRouter(tags=["app-settings"])


@router.get("/", response_model=AppSettingsResponse)
async def get_app_settings(
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
) -> AppSettingsResponse:
    return await service.get_settings(app_id)


@router.put("/", response_model=AppSettingsResponse)
async def update_app_settings(
    data: AppSettingsUpdate,
    _: Annotated[
        User,
        Depends(require_role([UserRole.ADMIN.value])),
    ],
    app_id: Annotated[str, Depends(get_app_id)],
    service: Annotated[AppSettingsService, Depends(get_app_settings_service)],
) -> AppSettingsResponse:
    return await service.update_settings(app_id, data)
