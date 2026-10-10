"""Асинхронный репозиторий настроек витрины по app_id."""

from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppSettings
from app.repositories.base import BaseRepository


class AppSettingsRepository(BaseRepository[AppSettings]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[AppSettings]:
        return AppSettings

    async def get_by_app_id(self, app_id: str) -> AppSettings | None:
        result = await self.session.execute(
            select(AppSettings).where(AppSettings.app_id == app_id)
        )
        return result.scalar_one_or_none()

    async def update_settings(
        self,
        app_id: str,
        data: Mapping[str, Any],
    ) -> AppSettings:
        settings = await self.get_by_app_id(app_id)
        if settings is None:
            settings = AppSettings(app_id=app_id)
            self.add(settings)

        for field, value in data.items():
            if field in {
                "store_name",
                "currency",
                "delivery_fee",
                "min_order_amount",
                "is_active",
                "extra_config",
            } and (value is not None or field == "extra_config"):
                setattr(settings, field, value)

        await self.session.commit()
        await self.session.refresh(settings)
        return settings
