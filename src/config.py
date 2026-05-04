from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, securely loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    github_token: str | None = None


def get_settings() -> Settings:
    """Lazy load settings and validate required configurations."""
    settings_instance = Settings()
    if not settings_instance.github_token:
        msg = "GITHUB_TOKEN is missing or empty in environment configuration."
        raise ValueError(msg)
    return settings_instance
