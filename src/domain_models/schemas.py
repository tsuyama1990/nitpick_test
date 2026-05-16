from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


def strip_extra_fields(data: dict[str, object], model_class: type[BaseModel]) -> dict[str, object]:
    """Pure function to strip out any fields not defined in the given Pydantic model's schema."""
    if not isinstance(data, dict):
        return data
    allowed_keys = model_class.model_fields.keys()
    return {k: v for k, v in data.items() if k in allowed_keys}


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    date: datetime

    @model_validator(mode="before")
    @classmethod
    def pre_validate(cls, data: dict[str, object]) -> dict[str, object]:
        return strip_extra_fields(data, cls)


class CommitData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: CommitAuthor

    @model_validator(mode="before")
    @classmethod
    def pre_validate(cls, data: dict[str, object]) -> dict[str, object]:
        return strip_extra_fields(data, cls)


class CommitItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commit: CommitData

    @model_validator(mode="before")
    @classmethod
    def pre_validate(cls, data: dict[str, object]) -> dict[str, object]:
        return strip_extra_fields(data, cls)
