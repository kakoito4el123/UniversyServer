"""Совместимость со старым путем импорта компонентов БД."""

from app.db.session import AsyncSessionLocal, engine, get_db

__all__ = ["AsyncSessionLocal", "engine", "get_db"]
