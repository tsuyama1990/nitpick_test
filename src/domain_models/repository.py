from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    owner: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)
