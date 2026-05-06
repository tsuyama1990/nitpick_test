from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    GITHUB_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    def __init__(self, **kwargs: Any) -> None:
        try:
            super().__init__(**kwargs)
        except Exception as exc:
            import pydantic
            if isinstance(exc, pydantic.ValidationError) and any(err['type'] == 'extra_forbidden' for err in exc.errors()):
                raise ValueError(str(exc)) from exc
            raise

_settings = None

def get_settings() -> AppConfig:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = AppConfig()
    return _settings
