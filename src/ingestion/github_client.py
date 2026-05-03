import httpx

from src.domain_models import AppConfig, CommitRecord, RepositoryMetadata
from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubClientError,
    RateLimitError,
    RepositoryNotFoundError,
)


class GitHubClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.base_url = "https://api.github.com"
        self.timeout = 10.0

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _handle_response_error(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            msg_auth = "Invalid GitHub token."
            raise AuthenticationError(msg_auth)
        if response.status_code == 403:
            msg_rate = "GitHub API rate limit exceeded or forbidden."
            raise RateLimitError(msg_rate)
        if response.status_code == 404:
            msg_not_found = "The requested repository was not found."
            raise RepositoryNotFoundError(msg_not_found)
        if response.status_code >= 400:
            msg_error = f"GitHub API error: {response.status_code} {response.text}"
            raise GitHubClientError(msg_error)

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        url = f"{self.base_url}/repos/{owner}/{repo}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._get_headers())

        if response.status_code != 200:
            self._handle_response_error(response)

        data = response.json()
        return RepositoryMetadata(
            owner=data["owner"]["login"],
            repo=data["name"],
            stargazers_count=data["stargazers_count"],
            forks_count=data["forks_count"],
            open_issues_count=data["open_issues_count"],
        )

    def get_commits(self, owner: str, repo: str) -> list[CommitRecord]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._get_headers(), params=params)

        if response.status_code != 200:
            self._handle_response_error(response)

        data = response.json()
        return [
            CommitRecord(
                sha=item["sha"],
                author_name=item["commit"]["author"]["name"],
                date=item["commit"]["author"]["date"],
            )
            for item in data
        ]
