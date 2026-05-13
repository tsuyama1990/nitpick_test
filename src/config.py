from functools import lru_cache

from src.domain_models import CacheConfig


@lru_cache
def get_settings() -> CacheConfig:
    return CacheConfig()
