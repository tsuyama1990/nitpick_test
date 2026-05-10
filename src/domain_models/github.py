from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepoInfo(BaseModel):
    """Basic information about a GitHub repository."""

    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Strip unknown keys before validation when extra='forbid'."""
        if not isinstance(data, dict):
            msg = "data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}


class Committer(BaseModel):
    """Information about a commit's author."""

    name: str = Field(min_length=1)
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            msg = "data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}


class CommitDetails(BaseModel):
    """Details inside a commit object."""

    committer: Committer
    message: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            msg = "data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}


class CommitInfo(BaseModel):
    """A commit in a GitHub repository."""

    sha: str = Field(min_length=1)
    commit: CommitDetails

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_extra(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            msg = "data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}
