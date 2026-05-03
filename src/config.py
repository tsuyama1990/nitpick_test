from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str | None = None
    cache_dir: Path = Path("./.cache")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Ensure cache dir exists
settings.cache_dir.mkdir(parents=True, exist_ok=True)
