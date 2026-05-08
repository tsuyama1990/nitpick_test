"""Manifest models for GitHub API data."""

from typing import Any

from pydantic import BaseModel, model_validator


class RepoInfo(BaseModel):
    """Repository information."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = {"extra": "forbid"}


class CommitInfo(BaseModel):
    """Commit information."""

    date: str
    committer: str

    model_config = {"extra": "forbid"}

    @classmethod
    def _extract_nested_fields(cls, commit: dict[str, Any], res: dict[str, Any]) -> None:
        """Extract fields from the nested commit dictionary."""
        author = commit.get("author", {})
        if isinstance(author, dict):
            date = author.get("date")
            if date is not None and "date" not in res:
                res["date"] = date

        committer = commit.get("committer", {})
        if isinstance(committer, dict):
            name = committer.get("name")
            if name is not None and "committer" not in res:
                res["committer"] = name

        # fallback for committer if not in commit.committer but in commit.author
        if "committer" not in res and isinstance(author, dict):
            name = author.get("name")
            if name is not None:
                res["committer"] = name

    @model_validator(mode="before")
    @classmethod
    def flatten_commit(cls, data: Any) -> Any:
        """Flatten nested commit data."""
        res: dict[str, Any] = {}
        if isinstance(data, dict):
            # To respect extra=forbid and parse Github response cleanly,
            # we rebuild the dict with ONLY the needed keys.
            if "date" in data:
                res["date"] = data["date"]
            if "committer" in data:
                res["committer"] = data["committer"]

            commit = data.get("commit", {})
            if isinstance(commit, dict):
                cls._extract_nested_fields(commit, res)
        return res
