from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Manifest placeholder for tracking system state."""

    version: str = "1.0.0"

    model_config = ConfigDict(extra="forbid")
