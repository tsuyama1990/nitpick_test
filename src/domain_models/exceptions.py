class GitHubAnalyticsError(Exception):
    """Base exception for GitHub Analytics application."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when a specified repository cannot be found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit is exceeded."""
