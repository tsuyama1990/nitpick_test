from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings
from src.domain_models.schemas import CommitAuthor, CommitItem


def test_commit_author_valid() -> None:
    data: dict[str, object] = {"name": "Alice", "date": "2023-10-01T10:00:00Z"}
    author = CommitAuthor(**data)  # type: ignore[arg-type]
    assert author.name == "Alice"
    assert isinstance(author.date, datetime)


def test_commit_author_invalid_missing_field() -> None:
    data: dict[str, object] = {"name": "Alice"}
    with pytest.raises(ValidationError):
        CommitAuthor(**data)  # type: ignore[arg-type]


def test_commit_author_extra_fields_stripped() -> None:
    data: dict[str, object] = {
        "name": "Alice",
        "date": "2023-10-01T10:00:00Z",
        "extra_field": "should be stripped",
    }
    # It should not raise ValidationError because of the extra fields strip function
    author = CommitAuthor(**data)  # type: ignore[arg-type]
    assert author.name == "Alice"
    assert not hasattr(author, "extra_field")


def test_commit_item_valid() -> None:
    data: dict[str, object] = {
        "commit": {
            "author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"},
            "message": "Update",  # should be stripped
        },
        "sha": "12345",  # should be stripped
    }

    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Alice"
    assert isinstance(item.commit.author.date, datetime)


def test_settings_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    get_settings.cache_clear()
    settings = Settings()
    assert settings.github_token == "test_token"  # noqa: S105
