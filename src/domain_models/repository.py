from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RepoMetrics(BaseModel):
    stars: int = Field(ge=0)
    forks: int = Field(ge=0)
    open_issues: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _extract_github_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Map GitHub API fields to our model if they are present and we are parsing raw dict
        # We only do mapping if we see 'stargazers_count' because if 'stars' is present,
        # it might be already formatted.
        extracted = data.copy()
        if "stargazers_count" in data:
            extracted["stars"] = data["stargazers_count"]
            extracted.pop("stargazers_count", None)
        if "forks_count" in data:
            extracted["forks"] = data["forks_count"]
            extracted.pop("forks_count", None)
        if "open_issues_count" in data:
            extracted["open_issues"] = data["open_issues_count"]
            extracted.pop("open_issues_count", None)

        # Remove extra keys that we don't care about to satisfy extra="forbid"
        allowed_keys = {"stars", "forks", "open_issues"}
        return {k: v for k, v in extracted.items() if k in allowed_keys}


class Commit(BaseModel):
    date: datetime
    author_name: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _extract_commit_data(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        extracted = data.copy()

        # GitHub API nested structure
        if "commit" in data and isinstance(data["commit"], dict):
            commit_info = data["commit"]
            if "author" in commit_info and isinstance(commit_info["author"], dict):
                author = commit_info["author"]
                if "date" in author:
                    extracted["date"] = author["date"]
                if "name" in author:
                    extracted["author_name"] = author["name"]

        allowed_keys = {"date", "author_name"}
        return {k: v for k, v in extracted.items() if k in allowed_keys}
