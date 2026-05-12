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
        """Strips out unknown keys before validation to safely parse GitHub API payloads."""
        if not isinstance(data, dict):
            msg = "Expected dictionary payload"
            raise TypeError(msg)

        commit_data = data.get("commit", {})
        if not isinstance(commit_data, dict):
            return {}

        author_data = commit_data.get("author", {})
        if not isinstance(author_data, dict):
            return {"commit": {}}

        stripped_author = {}
        if "name" in author_data:
            stripped_author["name"] = author_data["name"]
        if "date" in author_data:
            stripped_author["date"] = author_data["date"]

        return {"commit": {"author": stripped_author}}
