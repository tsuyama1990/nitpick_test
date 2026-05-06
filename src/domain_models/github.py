from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepositoryMetadata(BaseModel):
    """Represents core metadata for a GitHub repository."""

    owner: str = Field(..., description="The owner of the repository")
    name: str = Field(..., description="The name of the repository")
    star_count: int = Field(..., ge=0, alias="stargazers_count", description="The number of stars")
    fork_count: int = Field(..., ge=0, alias="forks_count", description="The number of forks")
    open_issue_count: int = Field(
        ..., ge=0, alias="open_issues_count", description="The number of open issues"
    )

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def extract_owner_login(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Extract the owner login from the nested owner object if present."""
        if isinstance(data, dict):
            owner_data = data.get("owner")
            if isinstance(owner_data, dict) and "login" in owner_data:
                data["owner"] = owner_data["login"]
        return data


class CommitRecord(BaseModel):
    """Represents a single commit record."""

    commit_hash: str = Field(..., alias="sha", description="The SHA hash of the commit")
    author_name: str = Field(..., description="The name of the author")
    date: datetime = Field(..., description="The timestamp of the commit")

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Extract nested fields from the GitHub commit payload."""
        if isinstance(data, dict):
            commit_data = data.get("commit")
            if isinstance(commit_data, dict):
                author_data = commit_data.get("author")
                if isinstance(author_data, dict):
                    if "name" in author_data and "author_name" not in data:
                        data["author_name"] = author_data["name"]
                    if "date" in author_data and "date" not in data:
                        data["date"] = author_data["date"]
        return data
