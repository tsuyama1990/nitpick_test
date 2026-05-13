import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Global configuration settings for the application."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), env_file_encoding="utf-8", extra="forbid"
    )

    # Cache Configuration
    cache_dir: Path = Field(
        default=Path(".cache"), description="Directory path for the local Parquet cache."
    )
    uat_cache_dir: Path = Field(
        default=Path(".uat_cache_dir"),
        description="Cache directory used specifically for User Acceptance Testing.",
    )
    default_cache_subdir: str = Field(
        default="cache", description="Default subdirectory name used in testing."
    )
