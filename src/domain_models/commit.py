from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sha: str
    author_name: str
    date: datetime

    @model_validator(mode="before")
    @classmethod
    def ensure_timezone_aware(cls, values: Any) -> Any:
        if isinstance(values, dict) and "date" in values:
            d = values["date"]
            if isinstance(d, datetime) and d.tzinfo is None:
                values["date"] = d.replace(tzinfo=UTC)
        return values
