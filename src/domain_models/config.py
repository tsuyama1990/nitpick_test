"""Configuration schema and loading logic for GitHub Analytics Dashboard."""

import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration defining all required environment variables."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=None, extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    """Singleton pattern to provide lazy evaluation and globally accessible cached configuration."""
    return Settings()  # type: ignore[call-arg]
