import pytest
from pydantic import ValidationError

from src.domain_models import get_config


def test_config_loading_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token_123")
    config = get_config()
    assert config.github_token == "fake_token_123"  # noqa: S105


def test_config_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        get_config()
