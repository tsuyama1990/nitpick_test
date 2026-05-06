from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


_settings: AppConfig | None = None


def get_settings() -> AppConfig:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = AppConfig()  # type: ignore[call-arg]
    return _settings
