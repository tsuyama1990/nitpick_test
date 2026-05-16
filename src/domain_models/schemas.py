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
    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitAuthor(BaseModel):
    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitData(BaseModel):
    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)


class CommitItem(BaseModel):
    commit: CommitData

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(cls, data)
