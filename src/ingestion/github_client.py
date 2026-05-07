import logging
from typing import Any

import httpx

from src.config import get_settings
from src.domain_models import CommitData, RepositoryInfo

# Setup logger to avoid leaking secrets
logger = logging.getLogger("httpx")
logger.setLevel(logging.WARNING)


class GitHubClientError(Exception):
    """Base class for GitHub Client exceptions."""


class AuthError(GitHubClientError):
    """Raised when authentication fails (HTTP 401)."""


class RateLimitError(GitHubClientError):
    """Raised when rate limit is exceeded (HTTP 403 or 429)."""


class NotFoundError(GitHubClientError):
    """Raised when the repository is not found (HTTP 404)."""


class GitHubClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.base_url = "https://api.github.com"

    def _check_response_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            msg = "Authentication failed. Please check your GITHUB_TOKEN."
            raise AuthError(msg)
        if response.status_code in {403, 429}:
            msg = "Rate limit exceeded."
            raise RateLimitError(msg)
        if response.status_code == 404:
            msg = "Repository not found."
            raise NotFoundError(msg)
        response.raise_for_status()

    def fetch_repository_info(self, owner: str, repo: str) -> RepositoryInfo:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url)
            self._check_response_status(response)
            data: dict[str, Any] = response.json()
            return RepositoryInfo(**data)

    def fetch_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitData]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url, params=params)
            self._check_response_status(response)
            data: list[dict[str, Any]] = response.json()
            return [CommitData(**item) for item in data]
