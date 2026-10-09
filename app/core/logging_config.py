"""Инициализация стандартного Python-логирования."""

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    """Настраивает формат и уровень логов приложения."""
    settings = get_settings()
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
