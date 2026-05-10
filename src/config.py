import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration management."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    """Provide a cached, singleton instance of the Settings."""
    return Settings()  # type: ignore[call-arg]
