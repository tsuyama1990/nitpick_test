from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommitItem(BaseModel):
    """Represents a single commit item."""

    model_config = ConfigDict(extra="forbid")

    date: datetime
    name: str
