from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositoryInfo(BaseModel):
    name: str = Field(alias="full_name")
    stars: int = Field(alias="stargazers_count")
    forks: int = Field(alias="forks_count")
    open_issues: int = Field(alias="open_issues_count")

    model_config = ConfigDict(extra="ignore")


class CommitDetail(BaseModel):
    sha: str
    message: str
    author_name: str
    author_date: datetime

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def extract_commit_info(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            commit = data.get("commit", {})
            author = commit.get("author", {})
            return {
                "sha": data.get("sha"),
                "message": commit.get("message"),
                "author_name": author.get("name"),
                "author_date": author.get("date"),
            }
        return data
