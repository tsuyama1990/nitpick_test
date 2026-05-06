from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class CommitData(BaseModel):
    sha: str
    author_name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def flatten_commit(cls, data: Any) -> Any:
        if isinstance(data, dict) and "commit" in data and isinstance(data["commit"], dict):
            commit = data["commit"]
            if "author" in commit and isinstance(commit["author"], dict):
                author = commit["author"]
                return {
                    "sha": data.get("sha"),
                    "author_name": author.get("name"),
                    "date": author.get("date"),
                }
        return data
