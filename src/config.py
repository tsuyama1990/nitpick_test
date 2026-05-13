from functools import lru_cache

from src.domain_models.config import AppSettings


@lru_cache
def get_settings() -> AppSettings:
    """Return a cached instance of the application settings."""
    return AppSettings()
