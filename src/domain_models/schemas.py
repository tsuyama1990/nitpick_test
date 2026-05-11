from typing import Any

from pydantic import BaseModel, ConfigDict


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    date: str


class CommitData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: CommitAuthor


class CommitItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commit: CommitData

    @classmethod
    def _strip_extra(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Strips out unknown keys before validation."""
        if not isinstance(data, dict):
            return data

        stripped = {}
        if "commit" in data and isinstance(data["commit"], dict):
            commit_data = data["commit"]
            stripped_commit = {}
            if "author" in commit_data and isinstance(commit_data["author"], dict):
                author_data = commit_data["author"]
                stripped_author = {}
                if "name" in author_data:
                    stripped_author["name"] = author_data["name"]
                if "date" in author_data:
                    stripped_author["date"] = author_data["date"]
                stripped_commit["author"] = stripped_author
            stripped["commit"] = stripped_commit

        return stripped
