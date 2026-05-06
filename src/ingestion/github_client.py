import logging
from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.github import CommitRecord, RepositoryMetadata

# Securely configure the logger to exclude sensitive headers
logger = logging.getLogger("httpx")
logger.setLevel(logging.WARNING)


class GitHubClient:
    """Client for fetching data from the GitHub REST API."""

    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        self.base_url = settings.GITHUB_API_BASE_URL
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Analysis-Dashboard",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        elif settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        self.client = httpx.Client(headers=self.headers, timeout=settings.HTTP_TIMEOUT)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | list[dict[str, Any]]:
        if response.status_code == 429:
            msg = "Rate limit exceeded."
            raise RateLimitError(msg)
        if response.status_code == 403:
            if response.headers.get("x-ratelimit-remaining") == "0":
                msg = "Rate limit exceeded."
                raise RateLimitError(msg)
            msg = "Forbidden."
            raise AuthenticationError(msg)
        if response.status_code == 401:
            msg = "Authentication failed."
            raise AuthenticationError(msg)
        if response.status_code == 404:
            msg = "Repository not found."
            raise RepositoryNotFoundError(msg)

        response.raise_for_status()

        res: dict[str, Any] | list[dict[str, Any]] = response.json()
        return res

    def fetch_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetch metadata for a specific repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.client.get(url)
        data = self._handle_response(response)

        if not isinstance(data, dict):
            msg = "Expected dictionary for repository metadata"
            raise TypeError(msg)

        return RepositoryMetadata.model_validate(data)

    def fetch_commit_history(self, owner: str, repo: str) -> list[CommitRecord]:
        """Fetch the latest 100 commits for a specific repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        response = self.client.get(url, params={"per_page": 100})
        data = self._handle_response(response)

        if not isinstance(data, list):
            msg = "Expected list for commit history"
            raise TypeError(msg)

        return [CommitRecord.model_validate(commit) for commit in data]
