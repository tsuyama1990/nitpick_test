from typing import Any

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_TOKEN: str
    GITHUB_API_URL: str = "https://api.github.com"
    HTTP_TIMEOUT: float = 10.0
    CACHE_TTL_SECONDS: int = 3600
    CACHE_DIR: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except pydantic.ValidationError as exc:
            if any(err["type"] == "extra_forbidden" for err in exc.errors()):
                msg = "Extra forbidden field"
                raise ValueError(msg) from exc
            raise


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
