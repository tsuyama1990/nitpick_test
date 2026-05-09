from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def _strip_extra(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            msg = "Data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_keys}

    @model_validator(mode="before")
    @classmethod
    def filter_extra_fields(cls, data: Any) -> Any:
        """Filters out extra fields from the API response before validation."""
        return cls._strip_extra(data)


class GitHubRepository(StrictBaseModel):
    owner: str
    name: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    @model_validator(mode="before")
    @classmethod
    def pre_filter_owner(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            msg = "Data must be a dictionary"
            raise TypeError(msg)

        data = dict(data)
        if "owner" in data and isinstance(data["owner"], dict) and "login" in data["owner"]:
            data["owner"] = data["owner"]["login"]
        elif "owner" in data and isinstance(data["owner"], str):
            pass  # already string, keep it

        # Delegate the rest to the base class stripping method
        return cls._strip_extra(data)


class GitHubCommitAuthor(StrictBaseModel):
    name: str
    email: str
    date: datetime


class GitHubCommitDetails(StrictBaseModel):
    author: GitHubCommitAuthor
    message: str


class GitHubCommit(StrictBaseModel):
    sha: str
    commit: GitHubCommitDetails
