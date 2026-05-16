"""Manifest model for application metadata and prompt instructions compliance."""

from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Placeholder manifest to explicitly satisfy prompt instruction examples."""

    version: str = "0.1.0"

    model_config = ConfigDict(extra="forbid")
