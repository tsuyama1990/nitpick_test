from datetime import datetime
from typing import Any

import httpx

from src.config import GITHUB_API_BASE_URL, GITHUB_API_TIMEOUT, get_github_token
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self) -> None:
        self.base_url = GITHUB_API_BASE_URL
        self.timeout = GITHUB_API_TIMEOUT

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {get_github_token()}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Translates HTTP errors into custom domain exceptions."""
        if response.status_code == 200:
            return

        if response.status_code == 404:
            msg = "The specified repository was not found."
            raise RepositoryNotFoundError(msg)
        if response.status_code == 401:
            msg = "Authentication failed. Invalid or expired token."
            raise AuthenticationError(msg)
        if response.status_code in (403, 429):
            if "rate limit" in response.text.lower() or response.status_code == 429:
                msg = "GitHub API rate limit exceeded."
                raise RateLimitError(msg)
            msg = f"GitHub API error: HTTP {response.status_code}"
            raise GitHubAPIError(msg)

        response.raise_for_status()

    def fetch_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetches metadata for a given GitHub repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._headers)
            self._handle_response_errors(response)

        data = response.json()
        return RepositoryMetadata(
            name=data["name"],
            owner=data["owner"]["login"],
            stargazers_count=data["stargazers_count"],
            forks_count=data["forks_count"],
            open_issues_count=data["open_issues_count"],
        )

    def fetch_latest_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitRecord]:
        """Fetches the latest commits for a given GitHub repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params: dict[str, Any] = {"per_page": limit}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._headers, params=params)
            self._handle_response_errors(response)

        data = response.json()
        commits = []
        for item in data:
            date_str = item["commit"]["author"]["date"].replace("Z", "+00:00")
            dt = datetime.fromisoformat(date_str)
            commit = CommitRecord(
                sha=item["sha"],
                author_name=item["commit"]["author"]["name"],
                date=dt,
            )
            commits.append(commit)
        return commits
