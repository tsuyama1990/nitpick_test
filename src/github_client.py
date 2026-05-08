import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClientError(Exception):
    pass


class RateLimitError(GitHubClientError):
    pass


class NotFoundError(GitHubClientError):
    pass


class AuthError(GitHubClientError):
    pass


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.client = httpx.Client(base_url=self.BASE_URL, headers=self.headers, timeout=10.0)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | list[dict[str, Any]]:
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

    def get_repo_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"/repos/{owner}/{repo}"
        res = self._handle_response(self.client.get(url))
        if not isinstance(res, dict):
            msg = "Expected dict"
            raise TypeError(msg)

        # Filter for strictly expected keys to satisfy extra="forbid" Pydantic models
        keys = ["stargazers_count", "forks_count", "open_issues_count"]
        return {k: res[k] for k in keys if k in res}

    def get_commits(self, owner: str, repo: str, per_page: int = 100) -> list[dict[str, Any]]:
        url = f"/repos/{owner}/{repo}/commits"
        res = self._handle_response(self.client.get(url, params={"per_page": per_page}))
        if not isinstance(res, list):
            msg = "Expected list"
            raise TypeError(msg)

        filtered_commits = []
        for c in res:
            try:
                author = c.get("commit", {}).get("author", {})
                filtered_commits.append({"name": author.get("name"), "date": author.get("date")})
            except AttributeError:
                pass
        return filtered_commits
