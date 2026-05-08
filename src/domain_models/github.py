"""GitHub domain models.

This module contains the Pydantic domain models for structuring the data
fetched from the GitHub REST API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetrics(BaseModel):
    """Domain model representing high-level repository metrics."""

    stargazers_count: int = Field(alias="stargazers_count", description="Number of stars")
    forks_count: int = Field(alias="forks_count", description="Number of forks")
    open_issues_count: int = Field(alias="open_issues_count", description="Number of open issues")

    model_config = ConfigDict(extra="forbid")


class Commit(BaseModel):
    """Domain model representing essential commit author data."""

    date: datetime = Field(description="Date and time of the commit")
    name: str = Field(description="Name of the committer")

    model_config = ConfigDict(extra="forbid")
