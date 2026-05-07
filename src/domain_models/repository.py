from pydantic import BaseModel, ConfigDict


class RepositoryInfo(BaseModel):
    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="ignore")
