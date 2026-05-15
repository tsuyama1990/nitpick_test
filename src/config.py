import functools
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="forbid")


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
