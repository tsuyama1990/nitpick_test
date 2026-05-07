from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class CommitData(BaseModel):
    author_name: str
    date: datetime

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def flatten_github_payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            commit = data.get("commit", {})
            author = commit.get("author", {})
            return {"author_name": author.get("name"), "date": author.get("date"), **data}
        return data
