from src.config import settings


def test_config_initialization() -> None:
    assert settings.CACHE_DIR == ".cache"
