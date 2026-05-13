import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    """Configuration settings for the caching layer."""

    CACHE_DIR: str = ".cache"
    CACHE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="forbid"
    )
