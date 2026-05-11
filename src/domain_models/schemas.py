from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            allowed_keys = set(cls.model_fields.keys())
            return {k: v for k, v in data.items() if k in allowed_keys}
        return data

    @model_validator(mode="before")
    @classmethod
    def strip_unknown_keys(cls, data: Any) -> Any:
        return cls._strip_extra(data)


class RepositoryMetrics(StrictBaseModel):
    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(StrictBaseModel):
    name: str
    date: datetime


class CommitData(StrictBaseModel):
    author: CommitAuthor


class CommitItem(StrictBaseModel):
    commit: CommitData
