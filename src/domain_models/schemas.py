"""Domain schemas for GitHub Analytics Dashboard."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra(data: Any, model_class: type[BaseModel]) -> Any:
    """Pure function to strip unknown keys from dictionary payloads before validation."""
    if isinstance(data, dict):
        allowed_fields = set(model_class.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_fields}
    return data


class RepositoryMetrics(BaseModel):
    """Container for GitHub repository KPI data."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitAuthor(BaseModel):
    """Author of a GitHub commit."""

    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitData(BaseModel):
    """Inner data payload of a GitHub commit."""

    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitItem(BaseModel):
    """Root item for a single commit returned by the GitHub API."""

    commit: CommitData

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)
