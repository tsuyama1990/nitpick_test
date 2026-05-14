import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    """Configuration for local file-system caching."""

    cache_dir: str = ".cache"
    cache_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="forbid",
    )
