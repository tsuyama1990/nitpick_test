"""GitHub API client module.

This module provides a client to interact with the GitHub REST API, fetching
repository metrics and commit data while handling common HTTP errors.
"""

import logging
from typing import Any

import httpx
from pydantic import BaseModel

from src.config import get_settings
from src.domain_models.github import Commit, RepositoryMetrics

logger = logging.getLogger(__name__)
# Suppress httpx info logs, especially to prevent leakage of auth headers
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClientError(Exception):
    """Base exception for all GitHub client errors."""


class RateLimitError(GitHubClientError):
    """Exception raised when the GitHub API rate limit is exceeded (HTTP 403 or 429)."""


class NotFoundError(GitHubClientError):
    """Exception raised when a repository or resource is not found (HTTP 404)."""


class AuthError(GitHubClientError):
    """Exception raised when authentication fails (HTTP 401)."""


class GitHubClient:
    """Client for fetching data from the GitHub REST API."""

    def __init__(self) -> None:
        """Initialize the client with settings, authentication headers, and an HTTP session."""
        self.settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.client = httpx.Client(
            base_url=self.settings.GITHUB_API_URL,
            headers=self.headers,
            timeout=self.settings.HTTP_TIMEOUT,
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | list[dict[str, Any]]:
        """Process the HTTP response and map specific status codes to domain exceptions."""
        if response.status_code == 404:
            msg = "Repository not found"
            raise NotFoundError(msg)
        if response.status_code == 401:
            msg = "Auth failed"
            raise AuthError(msg)
        if response.status_code in (403, 429):
            msg = "Rate limit exceeded"
            raise RateLimitError(msg)
        response.raise_for_status()
        res: dict[str, Any] | list[dict[str, Any]] = response.json()
        return res

    def _get_allowed_keys(self, model: type[BaseModel]) -> set[str]:
        """Precompute allowed keys for a given Pydantic model to optimize filtering."""
        allowed_keys = set(model.model_fields.keys())
        for field in model.model_fields.values():
            if field.alias:
                allowed_keys.add(field.alias)
        return allowed_keys

    def _filter_payload(self, payload: dict[str, Any], allowed_keys: set[str]) -> dict[str, Any]:
        """Filter payload to only include fields expected by the model using precomputed keys."""
        return {k: v for k, v in payload.items() if k in allowed_keys}

    def get_repo_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch the basic metrics for a specific GitHub repository."""
        url = f"/repos/{owner}/{repo}"
        res = self._handle_response(self.client.get(url))
        if not isinstance(res, dict):
            msg = "Expected dict"
            raise TypeError(msg)

        allowed_keys = self._get_allowed_keys(RepositoryMetrics)
        return self._filter_payload(res, allowed_keys)

    def get_commits(self, owner: str, repo: str, per_page: int = 100) -> list[dict[str, Any]]:
        """Fetch the most recent commits for a specific GitHub repository."""
        url = f"/repos/{owner}/{repo}/commits"
        res = self._handle_response(self.client.get(url, params={"per_page": per_page}))
        if not isinstance(res, list):
            msg = "Expected list"
            raise TypeError(msg)

        allowed_keys = self._get_allowed_keys(Commit)
        filtered_commits = []
        for c in res:
            try:
                author = c.get("commit", {}).get("author", {})
                filtered_commits.append(self._filter_payload(author, allowed_keys))
            except AttributeError:
                pass
        return filtered_commits
