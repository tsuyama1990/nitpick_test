from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GitHubRepository(BaseModel):
    owner: str
    name: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def filter_extra_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Filters out extra fields from the API response before validation."""
        if not isinstance(data, dict):
            msg = "Data must be a dictionary"
            raise TypeError(msg)
        allowed_keys = set(cls.model_fields.keys())
        # API maps to these, but owner is a dict, need to extract login and name

        filtered_data = {}
        if "owner" in data and isinstance(data["owner"], dict) and "login" in data["owner"]:
            filtered_data["owner"] = data["owner"]["login"]
        elif "owner" in data and isinstance(data["owner"], str):
            filtered_data["owner"] = data["owner"]

        for key in allowed_keys:
            if key in data and key != "owner":
                filtered_data[key] = data[key]

        return filtered_data


class GitHubCommitAuthor(BaseModel):
    name: str
    email: str
    date: datetime

    model_config = ConfigDict(extra="forbid")


class GitHubCommitDetails(BaseModel):
    author: GitHubCommitAuthor
    message: str

    model_config = ConfigDict(extra="forbid")


class GitHubCommit(BaseModel):
    sha: str
    commit: GitHubCommitDetails

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def filter_extra_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Filters out extra fields from the API response before validation."""
        if not isinstance(data, dict):
            msg = "Data must be a dictionary"
            raise TypeError(msg)

        # Optimization: Pre-compute allowed keys
        allowed_keys = set(cls.model_fields.keys())
        filtered_data = {k: v for k, v in data.items() if k in allowed_keys}

        # Filter inner commit object
        if "commit" in filtered_data and isinstance(filtered_data["commit"], dict):
            commit_allowed = set(GitHubCommitDetails.model_fields.keys())
            filtered_commit = {
                k: v for k, v in filtered_data["commit"].items() if k in commit_allowed
            }

            # Filter inner author object
            if "author" in filtered_commit and isinstance(filtered_commit["author"], dict):
                author_allowed = set(GitHubCommitAuthor.model_fields.keys())
                filtered_author = {
                    k: v for k, v in filtered_commit["author"].items() if k in author_allowed
                }
                filtered_commit["author"] = filtered_author

            filtered_data["commit"] = filtered_commit

        return filtered_data
