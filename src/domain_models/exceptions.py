class GitHubAnalyticsError(Exception):
    """Base class for all domain exceptions in GitHub Analytics."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when a specified repository cannot be found on GitHub."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit has been exceeded."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
