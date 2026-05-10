import tempfile

import pytest
from pytest_mock import MockerFixture

from src.config.settings import Settings


@pytest.fixture
def mock_settings(mocker: MockerFixture) -> Settings:
    # Patch the singleton accessor to return a settings instance with a dummy token
    # We must also ensure CACHE_DIR defaults to a safe temp dir to avoid IndexError due to missing permissions etc.
    settings = Settings(GITHUB_TOKEN="dummy", CACHE_DIR=tempfile.mkdtemp())  # noqa: S106
    mocker.patch("src.ingestion.github_client.get_settings", return_value=settings)
    mocker.patch("src.storage.cache.get_settings", return_value=settings)
    return settings
