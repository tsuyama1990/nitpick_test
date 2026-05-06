from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    GITHUB_TOKEN: str | None = None
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    HTTP_TIMEOUT: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a singleton instance of the settings."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        load_dotenv()
        _settings = Settings()
    return _settings
