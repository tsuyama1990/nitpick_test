from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, securely loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    github_token: str


# Instantiate settings immediately to fail fast if required config is missing
settings = Settings()  # type: ignore[call-arg]
