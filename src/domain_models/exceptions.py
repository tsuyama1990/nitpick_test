"""Custom exceptions for GitHub Analytics Dashboard."""


class GitHubAnalyticsError(Exception):
    """Base exception for all GitHub Analytics Dashboard errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Exception raised when a requested GitHub repository is not found."""



class RateLimitExceededError(GitHubAnalyticsError):
    """Exception raised when the GitHub API rate limit is exceeded."""
