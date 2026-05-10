from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class StrictBaseModel(BaseModel):
    """Base model that strictly enforces extra fields by stripping them."""

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        """Strip unknown fields before model instantiation."""
        if not isinstance(data, dict):
            return data

        allowed_keys = cls.model_fields.keys()
        return {k: v for k, v in data.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def pre_validate(cls, data: Any) -> Any:
        """Pydantic pre-validator to wrap the strip extra logic."""
        return cls._strip_extra(data)


class RepositoryMetrics(StrictBaseModel):
    """Metrics for a GitHub repository."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(StrictBaseModel):
    """Author of a GitHub commit."""

    name: str
    date: datetime


class CommitData(StrictBaseModel):
    """Core commit data from GitHub payload."""

    author: CommitAuthor


class CommitItem(StrictBaseModel):
    """Root item for a single commit array element."""

    commit: CommitData
