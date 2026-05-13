import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Global configuration settings for the application."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), env_file_encoding="utf-8", extra="forbid"
    )

    # Cache Configuration
    cache_dir: Path = Path(".cache")
