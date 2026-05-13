import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    """Configuration for local cache."""

    cache_dir: str = ".cache"

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="forbid")
