from pydantic import ValidationError

from src.domain_models import (
    Commit,
    InvalidPayloadError,
    RepositoryMetrics,
    filter_payload,
)
from src.ingestion.github_client import GitHubClient


class GitHubAnalyticsService:
    """Service to orchestrate GitHub data fetching and validation."""

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def get_metrics(self, owner: str, repo: str) -> RepositoryMetrics:
        """Fetches and validates repository metrics."""
        raw_data = self.client.get_repository_metrics(owner, repo)
        allowed_keys = set(RepositoryMetrics.model_fields.keys())
        filtered = filter_payload(raw_data, allowed_keys)

        try:
            return RepositoryMetrics(**filtered)
        except ValidationError as e:
            msg = f"Failed to validate repository metrics: {e}"
            raise InvalidPayloadError(msg) from e

    def get_commits(self, owner: str, repo: str, limit: int = 100) -> list[Commit]:
        """Fetches and validates recent commits."""
        raw_data = self.client.get_recent_commits(owner, repo, limit)
        allowed_keys = set(Commit.model_fields.keys())

        commits = []
        for item in raw_data:
            filtered = filter_payload(item, allowed_keys)
            try:
                commits.append(Commit(**filtered))
            except ValidationError as e:
                msg = f"Failed to validate commit payload: {e}"
                raise InvalidPayloadError(msg) from e

        return commits
