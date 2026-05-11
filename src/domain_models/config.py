import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), env_file_encoding="utf-8", extra="ignore"
    )
    default_top_n: int = 5


config = AppConfig()
