from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


def _strip_extra_fields(data: Any) -> Any:
    if not isinstance(data, dict):
        return data

    extracted = {}

    # GitHub API usually has a nested "commit" dict.
    if "commit" in data and isinstance(data["commit"], dict):
        commit_data = data["commit"]
        if "author" in commit_data and isinstance(commit_data["author"], dict):
            author_data = commit_data["author"]
            if "date" in author_data:
                extracted["date"] = author_data["date"]
            if "name" in author_data:
                extracted["name"] = author_data["name"]

    # Also support flat structure just in case, prioritizing the nested structure if found
    if "date" not in extracted and "date" in data:
        extracted["date"] = data["date"]
    if "name" not in extracted and "name" in data:
        extracted["name"] = data["name"]

    # If we couldn't extract standard github format, just return the data as is
    # and let Pydantic throw a ValidationError if required fields are missing
    if not extracted:
        return data

    return extracted


class CommitItem(BaseModel):
    date: str
    name: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def strip_extras(cls, data: Any) -> Any:
        return _strip_extra_fields(data)
