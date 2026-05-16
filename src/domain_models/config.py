from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    GITHUB_TOKEN: str
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_API_ACCEPT_HEADER: str = "application/vnd.github.v3+json"
    GITHUB_API_TIMEOUT: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
