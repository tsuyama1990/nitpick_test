from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class RepositoryMetrics(BaseModel):
    """Container for GitHub repository KPI data."""

    model_config = ConfigDict(extra="forbid")

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            error_msg = "Data must be a dictionary"
            raise TypeError(error_msg)
        return {k: v for k, v in data.items() if k in cls.model_fields}


class CommitAuthor(BaseModel):
    """Author details for a single commit."""

    model_config = ConfigDict(extra="forbid")

    name: str
    date: datetime

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            error_msg = "Data must be a dictionary"
            raise TypeError(error_msg)
        return {k: v for k, v in data.items() if k in cls.model_fields}


class CommitData(BaseModel):
    """Inner commit payload structure."""

    model_config = ConfigDict(extra="forbid")

    author: CommitAuthor

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            error_msg = "Data must be a dictionary"
            raise TypeError(error_msg)
        return {k: v for k, v in data.items() if k in cls.model_fields}


class CommitItem(BaseModel):
    """Root object for a single item in the commit array."""

    model_config = ConfigDict(extra="forbid")

    commit: CommitData

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            error_msg = "Data must be a dictionary"
            raise TypeError(error_msg)
        return {k: v for k, v in data.items() if k in cls.model_fields}
