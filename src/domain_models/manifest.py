# Manifest models for system state tracking, created to satisfy memory rule
from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    version: str
    model_config = ConfigDict(extra="forbid")
