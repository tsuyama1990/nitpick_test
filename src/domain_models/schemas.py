from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommitItem(BaseModel):
    """Schema for a single commit item."""

    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")
