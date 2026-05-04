import logging
from typing import Any

import httpx

from src.config import get_settings
from src.domain_models import CommitRecord, RepositoryMetadata
from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)

# Securely configure httpx logger to avoid leaking Authorization headers on debug
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClient:
    """
    Client for interacting with the GitHub REST API.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        """
        Initializes the client. Falls back to environment settings if token is not provided.
        """
        self._token = token or get_settings().github_token
        if not self._token:
            msg = "GitHub Token is missing. Please configure GITHUB_TOKEN."
            raise ValueError(msg)

        self.client = httpx.Client(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {self._token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10.0,
        )

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """
        Translates raw HTTP status codes to domain-specific exceptions.
        """
        if response.is_success:
            return

        if response.status_code in (401, 403):
            # 403 can also be rate limit, let's check for specific rate limit headers
            if "rate limit" in response.text.lower() or response.headers.get("x-ratelimit-remaining") == "0":
                msg = "GitHub API rate limit exceeded."
                raise RateLimitError(msg)
            msg = "Authentication failed. Invalid or expired GitHub token."
            raise AuthenticationError(msg)

        if response.status_code == 404:
            msg = "Requested repository was not found."
            raise RepositoryNotFoundError(msg)

        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded."
            raise RateLimitError(msg)

        msg = f"GitHub API request failed with status code {response.status_code}."
        raise GitHubAPIError(msg)

    def fetch_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """
        Fetches core metadata for a repository.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = self.client.get(url)
        self._handle_response_errors(response)

        data = response.json()
        return RepositoryMetadata(
            name=data["name"],
            owner=data["owner"]["login"],
            stargazers_count=data["stargazers_count"],
            forks_count=data["forks_count"],
            open_issues_count=data["open_issues_count"],
        )

    def fetch_commit_history(self, owner: str, repo: str) -> list[CommitRecord]:
        """
        Fetches the recent 100 commits from the repository.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        response = self.client.get(url, params={"per_page": 100})
        self._handle_response_errors(response)

        data: list[dict[str, Any]] = response.json()
        records: list[CommitRecord] = []
        for item in data:
            records.append(
                CommitRecord(
                    sha=item["sha"],
                    author_name=item["commit"]["author"]["name"],
                    date=item["commit"]["author"]["date"],
                )
            )
        return records
