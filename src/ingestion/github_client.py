import logging
from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.github import CommitInfo, RepoInfo

logging.getLogger("httpx").setLevel(logging.WARNING)

ERR_403 = "403 Forbidden"
ERR_404 = "404 Not Found"
ERR_429 = "429 Too Many Requests"


def get_repo_info(owner: str, repo: str) -> RepoInfo:
    settings = get_settings()
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 404:
            raise RuntimeError(ERR_404)
        if response.status_code == 403:
            raise RuntimeError(ERR_403)
        if response.status_code == 429:
            raise RuntimeError(ERR_429)
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        return RepoInfo(**data)


def get_commits(owner: str, repo: str) -> list[CommitInfo]:
    settings = get_settings()
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100"
    headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 404:
            raise RuntimeError(ERR_404)
        if response.status_code == 403:
            raise RuntimeError(ERR_403)
        if response.status_code == 429:
            raise RuntimeError(ERR_429)
        response.raise_for_status()

        data_list: list[dict[str, Any]] = response.json()
        return [CommitInfo(**item) for item in data_list]
