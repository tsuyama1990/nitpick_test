from typing import Any

import httpx

from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, token: str) -> None:
        self.client = httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self) -> "GitHubClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> None:
        """Handles HTTP response status codes and translates them to domain exceptions."""
        if response.status_code == 404:
            msg = f"Repository not found: {response.url}"
            raise RepositoryNotFoundError(msg)
        if response.status_code in (403, 429):
            msg = f"Rate limit exceeded: {response.status_code} - {response.text}"
            raise RateLimitExceededError(msg)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = f"Transport Error: {exc}"
            raise httpx.HTTPError(msg) from exc

    def get_repository_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        """
        Fetches core metrics for a specific repository.
        """
        response = self.client.get(f"/repos/{owner}/{repo}")
        self._handle_response(response)

        result = response.json()
        if not isinstance(result, dict):
            msg = "Expected a dictionary response from GitHub API for metrics."
            raise TypeError(msg)

        return result

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Fetches recent commits for a specific repository.
        """
        response = self.client.get(
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": limit},
        )
        self._handle_response(response)

        result = response.json()
        if not isinstance(result, list):
            msg = "Expected a list response from GitHub API for commits."
            raise TypeError(msg)

        return result
