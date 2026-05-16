from pydantic import BaseModel, ConfigDict


class RepositoryMetrics(BaseModel):
    """Core metrics for a GitHub repository."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")


class CommitHistory(BaseModel):
    """Represents a single commit history record."""

    sha: str
    date: str
    author: str

    model_config = ConfigDict(extra="forbid")
