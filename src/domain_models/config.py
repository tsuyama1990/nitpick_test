import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration contract for the application."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Provides a globally accessible, cached configuration instance."""
    return Settings()  # type: ignore[call-arg]
