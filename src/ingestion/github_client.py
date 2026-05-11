from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError


class GitHubClient:
    def __init__(self) -> None:
        settings = get_settings()
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {settings.github_token}",
        }
        self.client = httpx.Client(
            base_url=settings.github_api_base_url,
            headers=headers,
            timeout=settings.request_timeout,
        )

    def _handle_response(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            msg = "Repository not found."
            raise RepositoryNotFoundError(msg)
        if response.status_code in (403, 429):
            msg = "Rate limit exceeded."
            raise RateLimitExceededError(msg)
        response.raise_for_status()

    def get_repository_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"/repos/{owner}/{repo}"
        response = self.client.get(url)
        self._handle_response(response)
        return response.json()  # type: ignore[no-any-return]

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[dict[str, Any]]:
        url = f"/repos/{owner}/{repo}/commits"
        response = self.client.get(url, params={"per_page": limit})
        self._handle_response(response)
        return response.json()  # type: ignore[no-any-return]
