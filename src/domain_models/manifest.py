from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = "1.0.0"
