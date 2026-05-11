import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_TOKEN: str
    DEFAULT_COMMIT_LIMIT: int = 100
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="forbid")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
