from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


@lru_cache
def get_settings() -> Settings:
    """Returns a singleton instance of the application settings."""
    return Settings()  # type: ignore[call-arg]
