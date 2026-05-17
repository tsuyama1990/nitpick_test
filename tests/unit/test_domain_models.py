from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain_models.schemas import CommitItem


def test_commit_item_valid() -> None:
    data = {"name": "Alice", "date": "2024-05-17T10:00:00Z"}
    item = CommitItem(name=data["name"], date=data["date"])  # type: ignore[arg-type]
    assert item.name == "Alice"
    assert isinstance(item.date, datetime)


def test_commit_item_invalid_missing_field() -> None:
    data = {"name": "Alice"}
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


def test_commit_item_extra_fields_forbidden() -> None:
    data = {"name": "Alice", "date": "2024-05-17T10:00:00Z", "extra_field": "not_allowed"}
    with pytest.raises(ValidationError):
        CommitItem(name=data["name"], date=data["date"], extra_field=data["extra_field"])  # type: ignore[arg-type, call-arg]
