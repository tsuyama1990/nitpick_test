import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    """Configuration for local caching."""

    cache_dir: str = ".cache"
    ttl_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )
