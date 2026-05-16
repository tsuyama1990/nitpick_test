class GitHubAnalyticsError(Exception):
    """Base exception for GitHub Analytics application."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Exception raised when a GitHub repository is not found (e.g., 404)."""

    def __init__(self, message: str = "Repository not found") -> None:
        super().__init__(message)


class RateLimitExceededError(GitHubAnalyticsError):
    """Exception raised when the GitHub API rate limit is exceeded (e.g., 403 or 429)."""

    def __init__(self, message: str = "GitHub API rate limit exceeded") -> None:
        super().__init__(message)
