from typing import Any

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    # Target Project Secrets: GitHub Personal Access Token
    github_token: str | None = None

    # API Configuration
    github_base_url: str = "https://api.github.com"
    github_api_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="forbid", case_sensitive=False
    )

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as exc:
            # Detect extra field errors
            if any(err["type"] == "extra_forbidden" for err in exc.errors()):
                error_msg = ValueError("Extra inputs are not permitted")
                raise error_msg from exc
            raise


_settings: Settings | None = None


def get_settings() -> Settings:
    """Lazily load and return the application settings.

    Implements a module-level singleton pattern to prevent redundant
    .env parsing and instantiation overhead.
    """
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
