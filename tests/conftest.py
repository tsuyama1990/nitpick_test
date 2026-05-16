import pytest


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the environment variables for testing."""
    monkeypatch.setenv("GITHUB_TOKEN", "mock_ghp_token_for_testing")
