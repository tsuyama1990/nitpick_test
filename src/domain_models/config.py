import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CACHE_DIR: str = ".cache"
    CACHE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )


def get_settings() -> Settings:
    return Settings()
