from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    github_token: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_config() -> AppConfig:
    return AppConfig()  # type: ignore[call-arg]
