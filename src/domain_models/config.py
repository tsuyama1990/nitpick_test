from pydantic_settings import BaseSettings, SettingsConfigDict

_settings = None


class Settings(BaseSettings):
    CACHE_DIR: str = "./.cache"
    GITHUB_TOKEN: str | None = None
    CACHE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")


def get_settings() -> Settings:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
