import httpx

from src.config.settings import get_settings
from src.domain_models.repository import Commit, RepoMetrics


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


class GitHubAPIClient:
    def __init__(self) -> None:
        self.base_url = "https://api.github.com"
        self._setup_client()

    def _setup_client(self) -> None:
        settings = get_settings()
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        # Only add token if it's not empty string (useful for tests or public access sometimes, but we require it)
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

        # Initialize the httpx client. In real-world, we could keep a single session,
        # but for this script we will use client context manager per request or keep an instance.
        self.headers = headers

    def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.status_code == 200:
            return

        if response.status_code == 401:
            msg = "Authentication error: Invalid GitHub Token."
            raise GitHubAPIError(msg)
        if response.status_code == 403:
            msg = "Forbidden: Rate limit exceeded or access denied."
            raise GitHubAPIError(msg)
        if response.status_code == 404:
            msg = "Repository not found. Please check the owner/repo name."
            raise GitHubAPIError(msg)

        msg = f"GitHub API error: {response.status_code} - {response.text}"
        raise GitHubAPIError(msg)

    def fetch_repo_metrics(self, owner: str, repo: str) -> RepoMetrics:
        url = f"{self.base_url}/repos/{owner}/{repo}"

        with httpx.Client(headers=self.headers) as client:
            response = client.get(url)
            self._handle_response_errors(response)

            data = response.json()
            # type checking is handled by pydantic
            if not isinstance(data, dict):
                msg = "Expected dictionary response from GitHub API"
                raise TypeError(msg)

            return RepoMetrics(**data)

    def fetch_recent_commits(self, owner: str, repo: str) -> list[Commit]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}

        with httpx.Client(headers=self.headers) as client:
            response = client.get(url, params=params)
            self._handle_response_errors(response)

            data = response.json()
            if not isinstance(data, list):
                msg = "Expected list response from GitHub API"
                raise TypeError(msg)

            commits = []
            for item in data:
                commits.append(Commit(**item))

            return commits
