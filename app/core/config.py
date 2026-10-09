"""Загрузка и проверка настроек приложения."""

from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки читаются из переменных окружения и файла .env."""

    database_url: str
    secret_key: SecretStr
    debug: bool = False
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Добавляет драйвер asyncpg для стандартных PostgreSQL URL и разрешает SQLite."""
        if not isinstance(value, str):
            raise ValueError("DATABASE_URL должен быть строкой")

        if value.startswith("sqlite+aiosqlite://"):
            return value
        if value.startswith("sqlite:///"):
            return value.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        if value.startswith("sqlite://"):
            return value.replace("sqlite://", "sqlite+aiosqlite://", 1)

        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql+asyncpg://"):
            return value

        raise ValueError(
            "DATABASE_URL должен использовать PostgreSQL или SQLite"
        )

    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        """Не допускает пустой секретный ключ."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("SECRET_KEY не должен быть пустым")
        return value


@lru_cache
def get_settings() -> Settings:
    """Создает настройки один раз и повторно использует их в приложении."""
    return Settings()