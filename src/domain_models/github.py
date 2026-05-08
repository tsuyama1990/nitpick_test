from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepoInfo(BaseModel):
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="ignore")


class CommitInfo(BaseModel):
    date: datetime
    name: str

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def extract_author_info(cls, data: Any) -> Any:
        if isinstance(data, dict):
            commit = data.get("commit", {})
            if isinstance(commit, dict):
                author = commit.get("author", {})
                if isinstance(author, dict):
                    data["date"] = author.get("date")
                    data["name"] = author.get("name")
        return data
