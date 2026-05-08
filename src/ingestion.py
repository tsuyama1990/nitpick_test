import logging
from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.github import CommitInfo, RepositoryInfo

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    pass


class GitHubClient:
    def __init__(self) -> None:
        self.base_url = "https://api.github.com"
        self.settings = get_settings()

    def _get_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repository_info(self, owner: str, repo: str) -> RepositoryInfo:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        with httpx.Client() as client:
            try:
                response = client.get(url, headers=self._get_headers())
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
            data: dict[str, Any] = response.json()
            return RepositoryInfo(**data)

    def get_commits(self, owner: str, repo: str) -> list[CommitInfo]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}
        with httpx.Client() as client:
            try:
                response = client.get(url, headers=self._get_headers(), params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
            data_list: list[dict[str, Any]] = response.json()
            return [CommitInfo(**data) for data in data_list]

    def _handle_error(self, e: httpx.HTTPStatusError) -> None:
        status_code = e.response.status_code
        if status_code == 401:
            msg = "認証エラーが発生しました。トークンが有効か確認してください"
            raise GitHubClientError(msg) from e
        if status_code == 403:
            msg = "認証エラーが発生しました。トークンが有効か確認してください"
            raise GitHubClientError(msg) from e
        if status_code == 404:
            msg = "リポジトリが見つかりません。オーナー名とリポジトリ名を確認してください"
            raise GitHubClientError(msg) from e
        if status_code == 429:
            msg = "Rate limit exceeded"
            raise GitHubClientError(msg) from e
        msg = f"HTTP error {status_code}"
        raise GitHubClientError(msg) from e
