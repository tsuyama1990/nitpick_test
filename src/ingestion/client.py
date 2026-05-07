import logging
from typing import Any

import httpx

from src.config import get_settings
from src.domain_models import Commit, Repository

# Setup logger to not expose Authorization headers
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubClientError(Exception):
    pass


class GitHubClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> httpx.Response:
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}{endpoint}", headers=self.headers, params=params, timeout=10.0
                )
        except httpx.RequestError as e:
            err_msg = f"Network error during request: {e}"
            logger.exception(err_msg)
            raise GitHubClientError(err_msg) from e

        if response.status_code == 403:
            err_msg = "HTTP 403 Forbidden: Check your token or rate limit."
            logger.error(err_msg)
            raise GitHubClientError(err_msg)
        if response.status_code == 404:
            err_msg = "HTTP 404 Not Found: Repository does not exist."
            logger.error(err_msg)
            raise GitHubClientError(err_msg)
        if response.status_code == 429:
            err_msg = "HTTP 429 Too Many Requests: Rate limit exceeded."
            logger.error(err_msg)
            raise GitHubClientError(err_msg)

        response.raise_for_status()
        return response

    def get_repository_info(self, owner: str, repo: str) -> Repository:
        response = self._get(f"/repos/{owner}/{repo}")
        data = response.json()
        if not isinstance(data, dict):
            err_msg = "Response is not a dictionary"
            raise TypeError(err_msg)
        return Repository(**data)

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[Commit]:
        response = self._get(f"/repos/{owner}/{repo}/commits", params={"per_page": limit})
        data = response.json()
        if not isinstance(data, list):
            err_msg = "Response is not a list"
            raise TypeError(err_msg)
        return [Commit(**item) for item in data]
