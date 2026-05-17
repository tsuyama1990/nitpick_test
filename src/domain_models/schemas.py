from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommitItem(BaseModel):
    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")
