"""Domain schemas for GitHub Analytics."""

from collections.abc import Mapping
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra(data: object, model_fields: Mapping[str, object]) -> object:
    """Pure function to strip unknown keys before validation."""
    if not isinstance(data, dict):
        return data
    return {k: v for k, v in data.items() if k in model_fields}


class StrictModel(BaseModel):
    """Base model enforcing strict validation and extra stripping."""

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_unknown_fields(cls, data: object) -> object:
        """Strip unknown fields before model validation."""
        return _strip_extra(data, cls.model_fields)


class RepositoryMetrics(StrictModel):
    """Container for repository KPI data."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(StrictModel):
    """Author details for a commit."""

    name: str
    date: datetime


class CommitData(StrictModel):
    """Inner commit payload data."""

    author: CommitAuthor


class CommitItem(StrictModel):
    """Root object for a single item in the commit array."""

    commit: CommitData
