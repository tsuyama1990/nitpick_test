from src.domain_models.config import CacheSettings


def test_cache_settings() -> None:
    settings = CacheSettings(cache_dir="custom_dir", cache_ttl_seconds=120)
    assert settings.cache_dir == "custom_dir"
    assert settings.cache_ttl_seconds == 120
