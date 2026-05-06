from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator


class CommitData(BaseModel):
    sha: str
    author_name: str
    date: datetime

    @model_validator(mode="before")
    @classmethod
    def extract_nested_fields(cls, data: Any) -> Any:
        if isinstance(data, dict) and "commit" in data and isinstance(data["commit"], dict):
            commit_node = data["commit"]
            if "author" in commit_node and isinstance(commit_node["author"], dict):
                author_node = commit_node["author"]

                # Create a flattened dictionary
                flat_data = {
                    "sha": data.get("sha"),
                    "author_name": author_node.get("name"),
                    "date": author_node.get("date"),
                }

                # Copy over any other top-level fields that might be useful
                for key, value in data.items():
                    if key not in ("commit", "sha"):
                        flat_data[key] = value

                return flat_data
        return data
