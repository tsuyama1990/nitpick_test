from functools import lru_cache

from src.domain_models.config import AppConfig


@lru_cache(maxsize=1)
def get_settings() -> AppConfig:
    return AppConfig()
