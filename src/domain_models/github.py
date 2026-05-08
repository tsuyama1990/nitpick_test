from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepoInfo(BaseModel):
    """
    Repository information mapping GitHub API fields.
    API Docs: https://docs.github.com/en/rest/repos/repos#get-a-repository
    """

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="ignore")


class CommitInfo(BaseModel):
    """
    Commit information mapping GitHub API fields.
    API Docs: https://docs.github.com/en/rest/commits/commits#list-commits
    """

    sha: str
    committer_name: str = Field(..., description="Name of the committer")
    committer_date: datetime = Field(..., description="Date of the commit")

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def extract_committer_info(cls, data: Any) -> Any:
        if isinstance(data, dict):
            commit = data.get("commit", {})
            committer = commit.get("committer", {})
            if "committer_name" not in data and "name" in committer:
                data["committer_name"] = committer.get("name")
            if "committer_date" not in data and "date" in committer:
                data["committer_date"] = committer.get("date")
        return data
