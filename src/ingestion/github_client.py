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


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        self.client = httpx.Client(base_url="https://api.github.com", headers=headers, timeout=10.0)

    def _handle_response(self, response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            if response.status_code == 403 and "rate limit" in response.text.lower():
                msg = "GitHub API rate limit exceeded."
                raise RateLimitError(msg)
            msg = "Invalid or missing GitHub Personal Access Token."
            raise AuthenticationError(msg)
        if response.status_code == 404:
            msg = "The specified repository was not found on GitHub."
            raise RepositoryNotFoundError(msg)
        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded."
            raise RateLimitError(msg)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f"GitHub API request failed with status {e.response.status_code}"
            raise GitHubAPIError(msg) from e

    def fetch_repository_metadata(self, repo: str) -> RepositoryMetadata:
        try:
            response = self.client.get(f"/repos/{repo}")
        except httpx.RequestError as e:
            msg = f"Network error while connecting to GitHub: {e}"
            raise GitHubAPIError(msg) from e

        self._handle_response(response)

        data: dict[str, Any] = response.json()
        owner_data = data.get("owner", {})
        if isinstance(owner_data, dict):
            data["owner"] = owner_data.get("login", "")

        return RepositoryMetadata(**data)

    def fetch_latest_commits(self, repo: str) -> list[CommitRecord]:
        try:
            response = self.client.get(f"/repos/{repo}/commits", params={"per_page": 100})
        except httpx.RequestError as e:
            msg = f"Network error while connecting to GitHub: {e}"
            raise GitHubAPIError(msg) from e

        self._handle_response(response)

        data: list[dict[str, Any]] = response.json()
        commits = []
        for item in data:
            commit_data: dict[str, Any] = item.get("commit", {})
            author_data: dict[str, Any] = commit_data.get("author", {})

            commits.append(
                CommitRecord(
                    sha=item.get("sha", ""),
                    author=author_data.get("name", ""),
                    date=datetime.fromisoformat(
                        str(author_data.get("date", "")).replace("Z", "+00:00")
                    ),
                )
            )

        return commits
