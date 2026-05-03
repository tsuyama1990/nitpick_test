from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sha: str
    author_name: str
    date: datetime
