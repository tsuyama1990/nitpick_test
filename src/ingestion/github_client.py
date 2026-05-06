import logging
from typing import Any

import httpx

from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata

logger = logging.getLogger(__name__)

# Ensure HTTPX logger doesn't log sensitive headers
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClient:
    """A client to interact with the GitHub REST API."""

    BASE_URL = "https://api.github.com"
    TIMEOUT = 10.0

    def __init__(self, token: str | None = None) -> None:
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

        self.client = httpx.Client(headers=self.headers, timeout=self.TIMEOUT)

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Translates HTTP errors to custom domain exceptions."""
        if response.status_code == 404:
            msg = "Repository not found"
            raise RepositoryNotFoundError(msg)

        if response.status_code in (401, 403):
            # Check for rate limit
            is_rate_limit = response.status_code == 429
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get("x-ratelimit-remaining")
                if rate_limit_remaining == "0" or "API rate limit exceeded" in response.text:
                    is_rate_limit = True

            if is_rate_limit:
                msg = "GitHub API rate limit exceeded"
                raise RateLimitError(msg)
            msg = "Authentication failed: invalid or expired token"
            raise AuthenticationError(msg)

        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded"
            raise RateLimitError(msg)

        response.raise_for_status()

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetches the repository metadata."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        try:
            response = self.client.get(url)
            if response.is_error:
                self._handle_response_error(response)

            data: dict[str, Any] = response.json()
            return RepositoryMetadata(**data)
        except httpx.RequestError as exc:
            msg = f"Network error occurred: {exc}"
            raise GitHubAPIError(msg) from exc

    def get_commits(self, owner: str, repo: str, per_page: int = 100) -> list[CommitRecord]:
        """Fetches the commits for a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": per_page}
        try:
            response = self.client.get(url, params=params)
            if response.is_error:
                self._handle_response_error(response)

            data: list[dict[str, Any]] = response.json()
            return [CommitRecord(**commit_data) for commit_data in data]
        except httpx.RequestError as exc:
            msg = f"Network error occurred: {exc}"
            raise GitHubAPIError(msg) from exc
