from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_TOKEN: str | None = None
    DEFAULT_TOP_COMMITTERS: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
