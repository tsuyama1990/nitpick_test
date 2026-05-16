from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra(data: Any, model_cls: type[BaseModel]) -> Any:
    if not isinstance(data, dict):
        return data
    valid_keys = set(model_cls.model_fields.keys())
    return {k: v for k, v in data.items() if k in valid_keys}


class RepositoryMetrics(BaseModel):
    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitAuthor(BaseModel):
    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitData(BaseModel):
    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)


class CommitItem(BaseModel):
    commit: CommitData

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extra(cls, data: Any) -> Any:
        return _strip_extra(data, cls)
