from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Manifest file to satisfy the structural requirement check."""

    model_config = ConfigDict(extra="forbid")

    version: str
