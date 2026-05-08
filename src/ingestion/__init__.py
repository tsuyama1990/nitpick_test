"""Ingestion module for GitHub API."""

from .github_client import get_repo_commits, get_repo_info

__all__ = ["get_repo_commits", "get_repo_info"]
