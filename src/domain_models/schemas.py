from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class RepositoryMetrics(BaseModel):
    """Schema for core repository metrics."""

    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")


class Commit(BaseModel):
    """Schema for a single commit."""

    sha: str

    model_config = ConfigDict(extra="forbid")


def filter_payload(payload: dict[str, Any], allowed_keys: set[str]) -> dict[str, Any]:
    """Pure function to filter out unknown keys before Pydantic validation."""
    return {k: v for k, v in payload.items() if k in allowed_keys}
