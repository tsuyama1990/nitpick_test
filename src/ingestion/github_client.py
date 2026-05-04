from typing import Any

import httpx

from src.domain_models.exceptions import (
    AuthenticationError,
    GithubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata


class GithubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("GitHub token cannot be empty")
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.timeout = 10.0

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            raise RepositoryNotFoundError("Repository not found")
        if response.status_code in (401, 403):
            raise AuthenticationError("Authentication failed")
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        raise GithubAPIError(f"GitHub API returned error {response.status_code}")

    def fetch_repository_metadata(self, repo_name: str) -> RepositoryMetadata:
        url = f"{self.BASE_URL}/repos/{repo_name}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self.headers)
            data = self._handle_response(response)

            # Extract only fields needed for strict validation
            owner_login = ""
            if "owner" in data and isinstance(data["owner"], dict) and "login" in data["owner"]:
                owner_login = data["owner"]["login"]

            filtered_data = {
                "owner": owner_login,
                "name": data.get("name"),
                "stargazers_count": data.get("stargazers_count"),
                "forks_count": data.get("forks_count"),
                "open_issues_count": data.get("open_issues_count"),
            }

            return RepositoryMetadata(**filtered_data)

    def fetch_commits(self, repo_name: str) -> list[CommitRecord]:
        url = f"{self.BASE_URL}/repos/{repo_name}/commits"
        params = {"per_page": 100}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self.headers, params=params)
            data = self._handle_response(response)

            records = []
            for item in data:
                # Extract only fields needed for strict validation
                sha = item.get("sha")
                commit_data = item.get("commit", {})
                author_data = commit_data.get("author", {})

                filtered_item = {
                    "sha": sha,
                    "commit": {
                        "author": {
                            "name": author_data.get("name"),
                            "date": author_data.get("date"),
                        }
                    }
                }
                records.append(CommitRecord(**filtered_item))

            return records
