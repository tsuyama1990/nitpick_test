"""Pydantic schemas for the application."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class StrictModel(BaseModel):
    """Base model that forbids extra fields and strips unknown keys before validation."""

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        """Strip unknown keys before constructing the model instance."""
        if not isinstance(data, dict):
            return data

        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def validate_and_strip(cls, data: Any) -> Any:
        """Validator to strip unknown keys before instantiation."""
        return cls._strip_extra(data)


class RepositoryMetrics(StrictModel):
    """Repository metrics data."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(StrictModel):
    """Commit author data."""

    name: str
    date: datetime


class CommitData(StrictModel):
    """Inner commit payload."""

    author: CommitAuthor


class CommitItem(StrictModel):
    """A single item in the commit array returned by the API."""

    commit: CommitData
