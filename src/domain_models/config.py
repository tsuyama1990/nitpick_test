import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    """Configuration settings for the local caching system."""

    # Allows setting via CACHE_DIR environment variable, defaults to .cache
    cache_dir: str = Field(default=".cache", description="Directory to store cache files.")

    # Ensure environment variables are loaded appropriately
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), env_file_encoding="utf-8", extra="ignore"
    )


def get_cache_settings() -> CacheSettings:
    """Returns a singleton instance of the cache settings."""
    return CacheSettings()
