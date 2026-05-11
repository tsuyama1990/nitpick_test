from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.exceptions import (
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)


class GitHubClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 404:
            msg = f"Repository not found: {response.url}"
            raise RepositoryNotFoundError(msg)
        if response.status_code in (403, 429):
            msg = "GitHub API rate limit exceeded."
            raise RateLimitExceededError(msg)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f"GitHub API error: {e.response.status_code} - {e.response.text}"
            raise GitHubAnalyticsError(msg) from e

        result = response.json()
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result

        msg = f"Unexpected JSON response format: {type(result)}"
        raise GitHubAnalyticsError(msg)

    def get_repository_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url)
            result = self._handle_response(response)
            if not isinstance(result, dict):
                msg = "Expected dictionary response for metrics"
                raise GitHubAnalyticsError(msg)
            return result

    def get_recent_commits(
        self, owner: str, repo: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        actual_limit = limit if limit is not None else self.settings.DEFAULT_COMMIT_LIMIT
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": actual_limit}
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url, params=params)
            result = self._handle_response(response)
            if not isinstance(result, list):
                msg = "Expected list response for commits"
                raise GitHubAnalyticsError(msg)
            return result
