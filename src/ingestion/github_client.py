from datetime import datetime
from typing import Any

import httpx

from src.config import settings
from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata


class GithubClient:
    """Client for fetching data from the GitHub REST API securely and strictly."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        # Securely pass the authorization token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | list[dict[str, Any]]:
        """Handles HTTP response status codes strictly."""
        if response.status_code == 404:
            msg = "Repository not found"
            raise RepositoryNotFoundError(msg)
        if response.status_code in (401, 403):
            # Check for rate limit specifically
            if response.headers.get("X-RateLimit-Remaining") == "0":
                msg = "API rate limit exceeded"
                raise RateLimitError(msg)
            msg = "Authentication failed or forbidden. Check your token."
            raise AuthenticationError(msg)

        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetches repository metadata and parses it into a strict Pydantic model."""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
            response = client.get(url)
            data = self._handle_response(response)

            if isinstance(data, dict):
                return RepositoryMetadata(
                    owner=data["owner"]["login"],
                    repo=data["name"],
                    star_count=data["stargazers_count"],
                    fork_count=data["forks_count"],
                    open_issue_count=data["open_issues_count"],
                )
            msg = "Unexpected API response format for repository metadata"
            raise ValueError(msg)

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitRecord]:
        """Fetches the most recent commits and parses them into strict Pydantic models."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
            response = client.get(url, params=params)
            data = self._handle_response(response)

            if isinstance(data, list):
                return [
                    CommitRecord(
                        commit_hash=commit_data["sha"],
                        author_name=commit_data["commit"]["author"]["name"],
                        timestamp=datetime.fromisoformat(
                            commit_data["commit"]["author"]["date"].replace("Z", "+00:00")
                        ),
                    )
                    for commit_data in data
                ]
            msg = "Unexpected API response format for commits"
            raise ValueError(msg)
