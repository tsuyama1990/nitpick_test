import pytest
from pydantic import ValidationError

from src.domain_models import CommitItem, Manifest, Settings


def test_commit_item_valid() -> None:
    item = CommitItem(date="2023-10-27T10:00:00Z", name="Alice")  # type: ignore[arg-type]
    assert item.name == "Alice"


def test_commit_item_invalid() -> None:
    with pytest.raises(ValidationError, match="date"):
        CommitItem(date="invalid date", name="Alice")  # type: ignore[arg-type]


def test_commit_item_extra_forbid() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CommitItem(date="2023-10-27T10:00:00Z", name="Alice", extra_field="value")  # type: ignore[arg-type, call-arg]


def test_manifest_default_version() -> None:
    manifest = Manifest()
    assert manifest.version == "1.0.0"


def test_settings_missing_token() -> None:
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.GITHUB_TOKEN == "fake_token"  # noqa: S105
