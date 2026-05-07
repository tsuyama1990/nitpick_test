from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    GITHUB_TOKEN: str
    CACHE_TTL_SECONDS: int = 3600
    GITHUB_API_URL: str = "https://api.github.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)


_settings = None


def get_settings() -> AppConfig:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = AppConfig()  # type: ignore[call-arg]
    return _settings
