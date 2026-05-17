from datetime import datetime

from pydantic import BaseModel, ConfigDict


def strip_commit_item(data: dict[str, object]) -> dict[str, object]:
    """Strip extra fields from API payload before passing to model instantiation."""
    commit = data.get("commit")
    if not isinstance(commit, dict):
        return data

    author = commit.get("author")
    if not isinstance(author, dict):
        return {"commit": {}}

    return {
        "commit": {
            "author": {
                "name": author.get("name"),
                "date": author.get("date"),
            }
        }
    }


class RepositoryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    date: datetime


class CommitData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: CommitAuthor


class CommitItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commit: CommitData
