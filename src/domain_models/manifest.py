from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Manifest model for testing schemas and structure"""

    name: str
    version: str
    description: str

    model_config = ConfigDict(extra="forbid")
