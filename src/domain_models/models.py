from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1, alias="name")
    star_count: int = Field(ge=0, alias="stargazers_count")
    fork_count: int = Field(ge=0, alias="forks_count")
    open_issue_count: int = Field(ge=0, alias="open_issues_count")

    @model_validator(mode="before")
    @classmethod
    def extract_owner(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "owner" in data and isinstance(data["owner"], dict) and "login" in data["owner"]:
            data["owner"] = data["owner"]["login"]
        return data


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    commit_hash: str = Field(min_length=1, alias="sha")
    author_name: str = Field(min_length=1)
    date: datetime

    @model_validator(mode="before")
    @classmethod
    def extract_nested_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "commit" in data and isinstance(data["commit"], dict):
            commit_info = data["commit"]
            if "author" in commit_info and isinstance(commit_info["author"], dict):
                author_info = commit_info["author"]
                if "name" in author_info:
                    data["author_name"] = author_info["name"]
                if "date" in author_info:
                    data["date"] = author_info["date"]
        return data
