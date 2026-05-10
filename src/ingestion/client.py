from typing import Any

import httpx

from src.config.settings import get_settings
from src.domain_models.github import CommitInfo, RepoInfo


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response(self, response: httpx.Response) -> None:
        """Handles HTTP response status codes."""
        if response.status_code == 429:
            msg = "Rate limit exceeded (429)."
            raise GitHubAPIError(msg)
        if response.status_code == 403:
            msg = "Rate limit exceeded or access forbidden."
            raise GitHubAPIError(msg)
        if response.status_code == 404:
            msg = "Repository not found."
            raise GitHubAPIError(msg)
        if response.status_code == 401:
            msg = "Unauthorized. Please check your GitHub token."
            raise GitHubAPIError(msg)
        response.raise_for_status()

    def get_repo_info(self, owner: str, repo: str) -> RepoInfo:
        """Fetches basic information about a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            self._handle_response(response)
            data: dict[str, Any] = response.json()
            return RepoInfo(**data)

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitInfo]:
        """Fetches the recent commits of a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers, params=params)
            self._handle_response(response)
            data: list[dict[str, Any]] = response.json()
            return [CommitInfo(**commit_data) for commit_data in data]
