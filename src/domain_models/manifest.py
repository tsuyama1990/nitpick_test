from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Empty manifest model for system architecture requirements."""

    model_config = ConfigDict(extra="forbid")
