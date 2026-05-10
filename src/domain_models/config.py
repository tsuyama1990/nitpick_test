"""Configuration module for the application."""

import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()  # type: ignore[call-arg]
