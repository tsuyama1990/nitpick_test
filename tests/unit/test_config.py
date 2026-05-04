import pytest
from src.config import get_settings

def test_get_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError, match="GITHUB_TOKEN is missing or empty"):
        get_settings()
