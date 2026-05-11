from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class GitHubBaseModel(BaseModel):
    """Base model for GitHub schemas with extra key stripping."""

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            allowed_keys = set(cls.model_fields.keys())
            return {k: v for k, v in data.items() if k in allowed_keys}
        return data

    @model_validator(mode="before")
    @classmethod
    def strip_unknown_fields(cls, data: Any) -> Any:
        return cls._strip_extra(data)


class RepositoryMetrics(GitHubBaseModel):
    """Metrics for a GitHub repository."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(GitHubBaseModel):
    """Author of a GitHub commit."""

    name: str
    date: datetime


class CommitData(GitHubBaseModel):
    """Inner payload of a GitHub commit."""

    author: CommitAuthor


class CommitItem(GitHubBaseModel):
    """A single item in the commit array returned by the GitHub API."""

    commit: CommitData
