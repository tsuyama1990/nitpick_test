import logging
from datetime import datetime
from typing import Any

import httpx

from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)

# Explicitly configure httpx logger to avoid leaking Authorization headers
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize the GitHub API client.

        Args:
            token: Optional GitHub Personal Access Token for authentication.
        """
        self.token = token
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        self.client = httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=10.0,
        )

    def _handle_response(self, response: httpx.Response) -> None:
        """Centralized error handling for GitHub API responses."""
        if response.status_code in (401, 403):
            if response.status_code == 403 and "rate limit" in response.text.lower():
                msg = "GitHub API rate limit exceeded."
                logger.warning(msg)
                raise RateLimitError(msg)
            msg = "Invalid or missing GitHub Personal Access Token."
            logger.error("Authentication failed: %s", msg)
            raise AuthenticationError(msg)
        if response.status_code == 404:
            msg = "The specified repository was not found on GitHub."
            logger.warning(msg)
            raise RepositoryNotFoundError(msg)
        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded."
            logger.warning(msg)
            raise RateLimitError(msg)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f"GitHub API request failed with status {e.response.status_code}"
            logger.exception(msg)
            raise GitHubAPIError(msg) from e

    def fetch_repository_metadata(self, repo: str) -> RepositoryMetadata:
        """Fetch metadata for a specific GitHub repository.

        Args:
            repo: Repository identifier in the format 'owner/name'.

        Returns:
            RepositoryMetadata model containing strictly validated repository details.
        """
        logger.info("Fetching repository metadata for: %s", repo)
        try:
            response = self.client.get(f"/repos/{repo}")
        except httpx.RequestError as e:
            msg = f"Network error while connecting to GitHub: {e}"
            logger.exception(msg)
            raise GitHubAPIError(msg) from e

        self._handle_response(response)

        data: dict[str, Any] = response.json()
        owner_data = data.get("owner", {})
        owner_name = owner_data.get("login", "") if isinstance(owner_data, dict) else ""

        # Construct payload exactly matching the schema to satisfy extra="forbid"
        return RepositoryMetadata(
            owner=owner_name,
            name=str(data.get("name", "")),
            stars=int(data.get("stargazers_count", 0)),
            forks=int(data.get("forks_count", 0)),
            open_issues=int(data.get("open_issues_count", 0)),
        )

    def fetch_latest_commits(self, repo: str) -> list[CommitRecord]:
        """Fetch the latest commits for a given repository.

        Args:
            repo: Repository identifier in the format 'owner/name'.

        Returns:
            A list of strictly validated CommitRecord objects.
        """
        logger.info("Fetching latest commits for: %s", repo)
        try:
            response = self.client.get(f"/repos/{repo}/commits", params={"per_page": 100})
        except httpx.RequestError as e:
            msg = f"Network error while connecting to GitHub: {e}"
            logger.exception(msg)
            raise GitHubAPIError(msg) from e

        self._handle_response(response)

        data: list[dict[str, Any]] = response.json()
        commits = []
        for item in data:
            commit_data: dict[str, Any] = item.get("commit", {})
            author_data: dict[str, Any] = commit_data.get("author", {})

            date_str = str(author_data.get("date", "")).replace("Z", "+00:00")
            commits.append(
                CommitRecord(
                    hash=str(item.get("sha", "")),
                    author=str(author_data.get("name", "")),
                    date=datetime.fromisoformat(date_str),
                )
            )

        return commits
