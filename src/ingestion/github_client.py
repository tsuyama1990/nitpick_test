import logging

import httpx

from src.config import get_settings
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    DomainError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)

logger = logging.getLogger(__name__)
# Ensure sensitive headers are not logged by httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            token: GitHub Personal Access Token. Defaults to config.
            base_url: Base URL for the GitHub API. Defaults to config.
            timeout: HTTP request timeout in seconds. Defaults to config.
        """
        settings = get_settings()
        self.token = token or settings.github_token
        if not self.token:
            auth_error = AuthenticationError("GitHub token must be provided.")
            raise auth_error

        self.base_url = base_url or settings.github_base_url
        self.timeout = timeout if timeout is not None else settings.github_api_timeout

        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"token {self.token}",
        }

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle standard HTTP errors from GitHub API."""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 401:
                auth_error = AuthenticationError("Invalid or unauthorized GitHub token.")
                raise auth_error from e
            if status in (403, 429):
                # 403 can be rate limit or forbidden, 429 is explicitly rate limit
                rate_limit_error = RateLimitError("GitHub API rate limit exceeded.")
                raise rate_limit_error from e
            if status == 404:
                not_found_error = RepositoryNotFoundError("Repository not found.")
                raise not_found_error from e
            domain_error = DomainError(f"GitHub API error: {status}")
            raise domain_error from e

    def get_repository_metadata(self, owner_repo: str) -> RepositoryMetadata:
        """Fetch repository metadata.

        Args:
            owner_repo: The repository to fetch, formatted as 'owner/repo'.

        Returns:
            RepositoryMetadata object.
        """
        url = f"{self.base_url}/repos/{owner_repo}"
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(url, headers=self.headers)
            except httpx.RequestError as e:
                request_error = DomainError(f"HTTP request failed: {e}")
                raise request_error from e

            self._handle_response(response)

            data = response.json()
            return RepositoryMetadata(**data)

    def get_recent_commits(self, owner_repo: str, limit: int = 100) -> list[CommitRecord]:
        """Fetch recent commits for a repository.

        Args:
            owner_repo: The repository to fetch, formatted as 'owner/repo'.
            limit: Maximum number of commits to fetch (default 100).

        Returns:
            List of CommitRecord objects.
        """
        url = f"{self.base_url}/repos/{owner_repo}/commits"
        params = {"per_page": limit}

        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(url, headers=self.headers, params=params)
            except httpx.RequestError as e:
                request_error = DomainError(f"HTTP request failed: {e}")
                raise request_error from e

            self._handle_response(response)

            data = response.json()
            if not isinstance(data, list):
                format_error = DomainError("Unexpected GitHub API response format for commits.")
                raise format_error

            return [CommitRecord(**commit_data) for commit_data in data]
