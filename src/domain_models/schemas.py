from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class BaseDomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def strip_unknown_fields(cls, data: Any) -> Any:
        return cls._strip_extra(data)


class RepositoryMetrics(BaseDomainModel):
    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(BaseDomainModel):
    name: str
    date: datetime


class CommitData(BaseDomainModel):
    author: CommitAuthor


class CommitItem(BaseDomainModel):
    commit: CommitData
