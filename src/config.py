import functools
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_KEY = "ENV_FILE"
DEFAULT_ENV_FILE = ".env"


class Settings(BaseSettings):
    GITHUB_TOKEN: str
    CACHE_TTL: int = 3600
    CACHE_DIR: str = "./.cache"

    model_config = SettingsConfigDict(
        env_file=os.getenv(ENV_FILE_KEY, DEFAULT_ENV_FILE), extra="forbid"
    )


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
