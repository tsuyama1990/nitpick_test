from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class RepositoryMetrics(BaseModel):
    """Metrics for a GitHub repository."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k in cls.model_fields}
        return data


class CommitAuthor(BaseModel):
    """Author of a GitHub commit."""

    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k in cls.model_fields}
        return data


class CommitData(BaseModel):
    """Inner payload of a GitHub commit."""

    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k in cls.model_fields}
        return data


class CommitItem(BaseModel):
    """A single item in the commit array returned by the GitHub API."""

    commit: CommitData

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k in cls.model_fields}
        return data
