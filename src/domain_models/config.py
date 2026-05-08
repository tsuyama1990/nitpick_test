from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration using pydantic-settings.
    """

    GITHUB_TOKEN: str
    CACHE_DIR: str = str(Path.cwd() / ".cache" / "app")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")


_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Returns the settings instance (Singleton).
    """
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
