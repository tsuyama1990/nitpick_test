from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")

    GITHUB_TOKEN: str = Field(..., alias="GITHUB_TOKEN")
