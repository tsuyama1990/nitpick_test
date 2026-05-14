from src.domain_models.config import CacheSettings
from src.processing.cache import LocalCache


def main() -> None:
    settings = CacheSettings()
    cache = LocalCache(cache_dir=settings.cache_dir, ttl_seconds=settings.cache_ttl_seconds)
    print(f"Application initialized with cache dir {cache.cache_dir}")  # noqa: T201


if __name__ == "__main__":
    main()
