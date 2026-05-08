import logging
from typing import Any

import httpx

from src.domain_models import CommitInfo, RepoInfo, get_settings

logger = logging.getLogger(__name__)
# Securely configure the httpx logger to exclude sensitive Authorization headers
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubAPIClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, token: str | None = None) -> None:
        self.settings = get_settings()
        self.token = token or self.settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handles HTTP errors like rate limits and auth failures."""
        if response.status_code == 429:
            err_msg = "GitHub API rate limit exceeded (HTTP 429 Too Many Requests)."
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        if response.status_code == 403:
            # GitHub sometimes returns 403 for rate limits too, or forbidden
            err_msg = f"GitHub API Forbidden (HTTP 403). Possible rate limit or invalid token. Response: {response.text}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        if response.status_code == 401:
            err_msg = "GitHub API Unauthorized (HTTP 401). Invalid token."
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        if response.status_code == 404:
            err_msg = "Repository not found (HTTP 404). Please check owner and repository name."
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        response.raise_for_status()
        return response

    def get_repo_info(self, owner: str, repo: str) -> RepoInfo:
        """Fetches repository basic info."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        logger.info(f"Fetching repo info for {owner}/{repo}")

        with httpx.Client(headers=self.headers) as client:
            response = client.get(url)
            self._handle_response(response)
            data: dict[str, Any] = response.json()
            return RepoInfo(**data)

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitInfo]:
        """Fetches recent commits for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        logger.info(f"Fetching recent commits for {owner}/{repo}")

        with httpx.Client(headers=self.headers) as client:
            response = client.get(url, params={"per_page": limit})
            self._handle_response(response)
            data: list[dict[str, Any]] = response.json()
            return [CommitInfo(**commit) for commit in data]
