from functools import lru_cache

from src.domain_models import CacheConfig


@lru_cache
def get_cache_config() -> CacheConfig:
    return CacheConfig()
