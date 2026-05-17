from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Manifest settings."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0.0"
