from types import TracebackType
from typing import Self

import httpx

from src.domain_models.config import Settings
from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError
from src.domain_models.schemas import CommitHistory, RepositoryMetrics


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the GitHub API client using application settings."""
        if not settings.GITHUB_TOKEN:
            err_msg = "GitHub token must be provided via Settings"
            raise ValueError(err_msg)

        self.client = httpx.Client(
            base_url=settings.GITHUB_API_BASE_URL,
            headers={
                "Accept": settings.GITHUB_API_ACCEPT_HEADER,
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            },
            timeout=settings.GITHUB_API_TIMEOUT,
        )

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the client."""
        self.close()

    def _handle_response(self, response: httpx.Response, owner: str, repo: str) -> None:
        """Process the httpx.Response and translate HTTP errors into domain exceptions.

        Args:
            response: The raw response from the HTTP client.
            owner: The repository owner, used for error messages.
            repo: The repository name, used for error messages.

        Raises:
            RepositoryNotFoundError: If a 404 status code is returned.
            RateLimitExceededError: If a 403 or 429 status code is returned.
            httpx.HTTPStatusError: For other non-2xx status codes.
        """
        if response.status_code == 404:
            err_msg = f"Repository {owner}/{repo} not found."
            raise RepositoryNotFoundError(err_msg)
        if response.status_code in (403, 429):
            err_msg = "GitHub API rate limit exceeded."
            raise RateLimitExceededError(err_msg)
        response.raise_for_status()

    def get_repository_metrics(self, owner: str, repo: str) -> RepositoryMetrics:
        """Fetch core repository information metrics."""
        response = self.client.get(f"/repos/{owner}/{repo}")
        self._handle_response(response, owner, repo)
        data = response.json()
        return RepositoryMetrics(
            stargazers_count=data["stargazers_count"],
            forks_count=data["forks_count"],
            open_issues_count=data["open_issues_count"],
        )

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitHistory]:
        """Fetch recent commit history for the repository."""
        response = self.client.get(f"/repos/{owner}/{repo}/commits", params={"per_page": limit})
        self._handle_response(response, owner, repo)

        commits = []
        for item in response.json():
            commits.append(
                CommitHistory(
                    sha=item["sha"],
                    date=item["commit"]["author"]["date"],
                    author=item["commit"]["author"]["name"],
                )
            )
        return commits

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()
