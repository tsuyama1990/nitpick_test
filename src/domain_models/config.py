"""Configuration settings model."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings."""

    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the application settings."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
