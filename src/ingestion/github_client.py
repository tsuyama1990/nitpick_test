import httpx
from pydantic import ValidationError

from src.config import Settings
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubClientError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token if token is not None else Settings(_env_file=".env", _env_file_encoding="utf-8").github_token  # type: ignore[call-arg]
        self.base_url = "https://api.github.com"
        self.timeout = 10.0
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response_error(self, response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            msg = "Invalid authentication credentials."
            raise AuthenticationError(msg)
        if response.status_code == 404:
            msg = "Repository not found."
            raise RepositoryNotFoundError(msg)
        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded."
            raise RateLimitError(msg)

        response.raise_for_status()

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = httpx.get(url, headers=self.headers, timeout=self.timeout)
            self._handle_response_error(response)
            data = response.json()
        except httpx.RequestError as e:
            msg = f"Request failed: {e}"
            raise GitHubClientError(msg) from e
        else:
            try:
                # Filter down to just the fields we want to validate according to strict schema
                filtered_data = {
                    "owner": data.get("owner", {}),
                    "name": data.get("name"),
                    "stargazers_count": data.get("stargazers_count"),
                    "forks_count": data.get("forks_count"),
                    "open_issues_count": data.get("open_issues_count"),
                }
                model = RepositoryMetadata.model_validate(filtered_data)
            except ValidationError as e:
                msg = f"Invalid repository metadata response: {e}"
                raise GitHubClientError(msg) from e
            else:
                return model

    def get_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitRecord]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": min(limit, 100)}

        try:
            response = httpx.get(url, headers=self.headers, params=params, timeout=self.timeout)
            self._handle_response_error(response)
            data = response.json()
        except httpx.RequestError as e:
            msg = f"Request failed: {e}"
            raise GitHubClientError(msg) from e
        else:
            try:
                commits = []
                for item in data:
                    filtered_item = {
                        "sha": item.get("sha"),
                        "commit": item.get("commit", {}),
                    }
                    commits.append(CommitRecord.model_validate(filtered_item))
            except ValidationError as e:
                msg = f"Invalid commit record response: {e}"
                raise GitHubClientError(msg) from e
            else:
                return commits
