import logging
from typing import Any

import httpx

from src.config import get_settings
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)

# Securely configure httpx logger to warn to avoid exposing secrets
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClient:
    """Client for safely fetching data from the GitHub REST API."""

    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        self.base_url = settings.GITHUB_API_BASE_URL
        self.timeout = settings.GITHUB_API_TIMEOUT

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        token = token or settings.GITHUB_TOKEN
        if token:
            # Requirements explicitly demand "token {token}" or generic bearer
            # GitHub usually uses "Bearer {token}" but prompt memory asks for "token {token}"
            self.headers["Authorization"] = f"token {token}"

        self.client = httpx.Client(headers=self.headers, timeout=self.timeout)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Parses the response and intercepts HTTP errors to raise custom domain exceptions."""
        status_code = response.status_code

        if status_code == 200:
            return response.json()

        if status_code in (401, 403):
            # Check for rate limit which can also return 403
            if response.headers.get("x-ratelimit-remaining") == "0":
                msg = "GitHub API rate limit exceeded."
                raise RateLimitError(msg)
            msg = "Authentication failed. Invalid or expired token."
            raise AuthenticationError(msg)

        if status_code == 404:
            msg = "The requested repository could not be found."
            raise RepositoryNotFoundError(msg)

        if status_code == 429:
            msg = "GitHub API rate limit exceeded (Too Many Requests)."
            raise RateLimitError(msg)

        msg = f"Unexpected API error: {status_code} {response.text}"
        raise GitHubAPIError(msg)

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetches metadata for a given GitHub repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.client.get(url)
        data = self._handle_response(response)

        # Pydantic handles validation and aliases gracefully.
        return RepositoryMetadata(**data)

    def get_recent_commits(self, owner: str, repo: str, count: int = 100) -> list[CommitRecord]:
        """Fetches the most recent commits for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": count}
        response = self.client.get(url, params=params)
        data_list = self._handle_response(response)

        commits = []
        for item in data_list:
            commits.append(CommitRecord(**item))

        return commits
