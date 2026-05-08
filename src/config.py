"""Application configuration module.

This module manages the application's configuration by loading variables from the
environment or a `.env` file into a strictly typed Pydantic `BaseSettings` model.
"""

from typing import Any

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strictly typed settings model for the application."""

    GITHUB_TOKEN: str
    GITHUB_API_URL: str = "https://api.github.com"
    HTTP_TIMEOUT: float = 10.0
    CACHE_TTL_SECONDS: int = 3600
    CACHE_DIR: str | None = None
    CACHE_FILE_SUFFIX: str = ".parquet"
    CACHE_KEY_SEPARATOR: str = "_"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    def __init__(self, **data: Any) -> None:
        """Initialize settings and handle specific validation errors."""
        try:
            super().__init__(**data)
        except pydantic.ValidationError as exc:
            if any(err["type"] == "extra_forbidden" for err in exc.errors()):
                msg = "Extra forbidden field"
                raise ValueError(msg) from exc
            raise


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the application settings (Singleton pattern)."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
