import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from the environment.
    Strictly forbids extra inputs to prevent configuration drift.
    """

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Provides a cached singleton instance of Settings."""
    return Settings()  # type: ignore[call-arg]
