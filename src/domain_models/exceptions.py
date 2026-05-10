class GitHubAnalyticsError(Exception):
    """Base class for all domain exceptions."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when a specified repository cannot be found on GitHub."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit has been exceeded."""
