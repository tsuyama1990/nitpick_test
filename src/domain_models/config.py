import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    cache_dir: str = ".cache"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), extra="forbid", env_file_encoding="utf-8"
    )
