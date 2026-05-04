from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    owner: str = Field(validation_alias=AliasPath("owner", "login"))
    name: str
    stars: int = Field(ge=0, validation_alias="stargazers_count")
    forks: int = Field(ge=0, validation_alias="forks_count")
    open_issues: int = Field(ge=0, validation_alias="open_issues_count")


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    hash: str = Field(validation_alias="sha")
    author: str = Field(validation_alias=AliasPath("commit", "author", "name"))
    date: datetime = Field(validation_alias=AliasPath("commit", "author", "date"))
