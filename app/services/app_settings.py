"""Бизнес-логика настроек витрины с мягким фоллбэком."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppSettings
from app.repositories.app_settings import AppSettingsRepository
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdate


class AppSettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.settings = AppSettingsRepository(session)

    async def get_settings(self, app_id: str) -> AppSettingsResponse:
        settings = await self.settings.get_by_app_id(app_id)
        if settings is None:
            return AppSettingsResponse(app_id=app_id)
        return AppSettingsResponse.model_validate(settings)

    async def update_settings(
        self,
        app_id: str,
        data: AppSettingsUpdate,
    ) -> AppSettingsResponse:
        settings: AppSettings = await self.settings.update_settings(
            app_id,
            data.model_dump(exclude_unset=True),
        )
        return AppSettingsResponse.model_validate(settings)
