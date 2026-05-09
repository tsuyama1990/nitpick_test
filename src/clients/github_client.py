import httpx

from src.domain_models.config import get_settings
from src.domain_models.github import CommitInfo, RepoInfo


class GitHubClientError(Exception):
    """Custom exception for GitHub API errors."""


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repo_info(self, owner: str, repo: str) -> RepoInfo:
        """Fetches basic information about a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        with httpx.Client() as client:
            res = client.get(url, headers=self.headers)
            self._check_response(res)

            data = res.json()
            if not isinstance(data, dict):
                msg = "Expected dict from GitHub API for repo info"
                raise TypeError(msg)

            return RepoInfo.model_validate(data)

    def get_commits(self, owner: str, repo: str) -> list[CommitInfo]:
        """Fetches the last 100 commits for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}
        with httpx.Client() as client:
            res = client.get(url, headers=self.headers, params=params)
            self._check_response(res)

            data = res.json()
            if not isinstance(data, list):
                msg = "Expected list of commits from GitHub API"
                raise TypeError(msg)

            return [CommitInfo.model_validate(c) for c in data]

    def _check_response(self, response: httpx.Response) -> None:
        """Checks the response for errors like 403, 404, or 429."""
        if response.status_code in (403, 429):
            msg = f"Rate limit exceeded or access forbidden: {response.status_code}"
            raise GitHubClientError(msg)
        if response.status_code == 404:
            msg = "Repository not found"
            raise GitHubClientError(msg)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f"HTTP error occurred: {e}"
            raise GitHubClientError(msg) from e
