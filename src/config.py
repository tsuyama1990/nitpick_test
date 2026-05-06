from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    GITHUB_TOKEN: str | None = None


_settings: Settings | None = None


def get_settings() -> Settings:
    """Returns the application settings. Instantiates it lazily as a singleton."""
    global _settings  # noqa: PLW0603

    if _settings is None:
        _settings = Settings()

    return _settings
