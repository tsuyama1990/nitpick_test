"""Application configuration management."""

import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    GITHUB_TOKEN: str


@functools.lru_cache
def get_settings() -> Settings:
    """Provide a cached, singleton instance of the application settings."""
    return Settings()  # type: ignore[call-arg]
