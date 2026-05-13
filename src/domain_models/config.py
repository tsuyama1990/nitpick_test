import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    """Configuration for the local caching system."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )

    cache_dir: Path = Path(".cache")
    cache_ttl_seconds: int = 3600
