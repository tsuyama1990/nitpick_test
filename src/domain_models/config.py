import functools
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of the Settings class."""
    return Settings()  # type: ignore[call-arg]
