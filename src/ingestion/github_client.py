from typing import Any

import httpx

from src.domain.exceptions import RateLimitExceededError, RepositoryNotFoundError


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
            msg = "Repository not found."
            raise RepositoryNotFoundError(msg)
        if response.status_code in (403, 429):
            msg = "Rate limit exceeded."
            raise RateLimitExceededError(msg)
        response.raise_for_status()
        return response.json()

    def get_repository_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        response = self.client.get(f"repos/{owner}/{repo}")
        result = self._handle_response(response)
        if not isinstance(result, dict):
            msg = "Expected dict from API"
            raise TypeError(msg)
        return result

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[dict[str, Any]]:
        response = self.client.get(f"repos/{owner}/{repo}/commits", params={"per_page": limit})
        result = self._handle_response(response)
        if not isinstance(result, list):
            msg = "Expected list from API"
            raise TypeError(msg)
        return result
