from pydantic import BaseModel, ConfigDict


class RepositoryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    email: str
    date: str


class CommitDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: CommitAuthor
    message: str


class CommitItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sha: str
    commit: CommitDetail
