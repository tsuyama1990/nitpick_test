import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the environment variables for testing config loading without a real .env."""
    monkeypatch.setenv("GITHUB_TOKEN", "mock_token_for_tests")
