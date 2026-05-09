import logging

import httpx

from src.domain_models import Commit, Repository, get_settings

logger = logging.getLogger(__name__)
# Ensure token is never logged by httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


class GitHubAPIError(Exception):
    pass


class RateLimitError(GitHubAPIError):
    pass


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {self.settings.GITHUB_TOKEN}"
        return headers

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        if response.status_code in (403, 429):
            msg = "Rate limit exceeded or access forbidden."
            raise RateLimitError(msg)
        if not response.is_success:
            msg = f"API request failed with status {response.status_code}: {response.text}"
            raise GitHubAPIError(msg)
        return response

    def get_repository_info(self, owner: str, repo: str) -> Repository:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers())
            self._handle_response(response)
            data = response.json()
            if not isinstance(data, dict):
                msg = "Expected response to be a JSON object"
                raise TypeError(msg)
            return Repository.from_api_payload(data)

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[Commit]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers(), params=params)
            self._handle_response(response)
            data = response.json()
            if not isinstance(data, list):
                msg = "Expected response to be a JSON array"
                raise TypeError(msg)
            return [Commit.from_api_payload(item) for item in data if isinstance(item, dict)]
