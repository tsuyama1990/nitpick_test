from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra(cls: type[BaseModel], data: Any) -> Any:
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k in cls.model_fields}
    return data

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
