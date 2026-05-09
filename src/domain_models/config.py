import os
import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

_settings: "Settings | None" = None


class Settings(BaseSettings):
    GITHUB_TOKEN: str
    CACHE_DIR: pathlib.Path = pathlib.Path(
        os.getenv("CACHE_DIR", pathlib.Path.cwd() / ".cache" / "app")
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )


def get_settings() -> Settings:
    """Lazy initialization of the settings singleton."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
