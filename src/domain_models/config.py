"""Configuration schema and loading logic for GitHub Analytics Dashboard."""

import functools
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.getenv("ENV_FILE", ".env")


class Settings(BaseSettings):
    """Application configuration defining all required environment variables."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8", extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    """Singleton pattern to provide lazy evaluation and globally accessible cached configuration."""
    return Settings()  # type: ignore[call-arg]
