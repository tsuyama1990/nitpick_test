from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra(cls: Any, data: Any) -> Any:
    """Strip unknown keys from the payload before constructing the model instance."""
    if not isinstance(data, dict):
        return data

    # We only keep keys that are defined in the model fields
    valid_keys = cls.model_fields.keys()
    return {k: v for k, v in data.items() if k in valid_keys}


class RepositoryMetrics(BaseModel):
    """Container for essential repository KPI metrics from GitHub."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitAuthor(BaseModel):
    """Represents the author of a commit, including their name and the commit timestamp."""

    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitData(BaseModel):
    """Contains the inner data of a single commit, matching GitHub's nested payload structure."""

    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitItem(BaseModel):
    """Represents a single commit item in the array returned by the GitHub API."""

    commit: CommitData

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)
