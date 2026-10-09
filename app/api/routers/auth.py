"""Совместимый импорт auth-роутера из API v1."""

from app.api.v1.endpoints.auth import router

__all__ = ["router"]
