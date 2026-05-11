import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    github_token: str

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of Settings."""
    return Settings()  # type: ignore[call-arg]
