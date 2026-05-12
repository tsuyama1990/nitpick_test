import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Cache Configuration
    cache_dir: str = ".cache"
    cache_ttl: int = 3600
    uat_cache_root: str = "tests/uat/.test_cache"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Retrieve the application settings."""
    return Settings()
