from typing import Any

import httpx

from src.domain_models import RateLimitExceededError, RepositoryNotFoundError


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.client = httpx.Client(
            base_url="https://api.github.com/",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10.0,
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 404:
            msg = "Repository not found"
            raise RepositoryNotFoundError(msg)
        if response.status_code in (403, 429):
            msg = "API rate limit exceeded"
            raise RateLimitExceededError(msg)
        response.raise_for_status()
        return response.json()

    def get_repository_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        response = self.client.get(f"repos/{owner}/{repo}")
        data = self._handle_response(response)
        if not isinstance(data, dict):
            msg = "Expected dictionary response for metrics"
            raise TypeError(msg)
        return data

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[dict[str, Any]]:
        response = self.client.get(f"repos/{owner}/{repo}/commits", params={"per_page": limit})
        data = self._handle_response(response)
        if not isinstance(data, list):
            msg = "Expected list response for commits"
            raise TypeError(msg)
        return data

    def close(self) -> None:
        self.client.close()
