from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    github_token: str = Field(min_length=1, description="GitHub Personal Access Token")


def get_settings() -> Settings:
    """Returns the application settings."""
    return Settings() # type: ignore[call-arg]

# Export a function to get settings, which will be called when needed.
