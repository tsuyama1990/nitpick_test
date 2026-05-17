from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    github_token: str = Field(..., alias="GITHUB_TOKEN", description="GitHub API token")

    model_config = SettingsConfigDict(extra="forbid", env_file=".env", env_file_encoding="utf-8")
