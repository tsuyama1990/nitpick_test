from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositoryMetadata(BaseModel):
    """Represents the core metadata of a GitHub repository."""

    owner: str = Field(..., description="The owner of the repository")
    repo_name: str = Field(..., alias="name", description="The name of the repository")
    star_count: int = Field(..., alias="stargazers_count", ge=0, description="Number of stars")
    fork_count: int = Field(..., alias="forks_count", ge=0, description="Number of forks")
    open_issue_count: int = Field(
        ..., alias="open_issues_count", ge=0, description="Number of open issues"
    )

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def extract_owner(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Extract owner login if owner is a dict (standard GitHub API response)."""
        if isinstance(data, dict) and "owner" in data and isinstance(data["owner"], dict):
            data["owner"] = data["owner"].get("login", "")
        return data


class CommitRecord(BaseModel):
    """Represents a single commit record."""

    commit_hash: str = Field(..., alias="sha", description="The commit SHA hash")
    author_name: str = Field(..., description="The author's name")
    timestamp: datetime = Field(..., description="The timestamp of the commit")

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_github_commit(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested GitHub commit data into the expected fields."""
        if not isinstance(data, dict) or "commit" not in data:
            return data

        commit_data = data["commit"]
        if not isinstance(commit_data, dict) or "author" not in commit_data:
            return data

        author_data = commit_data["author"]
        if not isinstance(author_data, dict):
            return data

        # Only set if not already present
        if "author_name" not in data:
            data["author_name"] = author_data.get("name", "")
        if "timestamp" not in data:
            data["timestamp"] = author_data.get("date", "")
        return data
