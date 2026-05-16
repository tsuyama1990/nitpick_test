"""Domain exceptions for GitHub Analytics."""


class GitHubAnalyticsError(Exception):
    """Base exception for GitHub Analytics business logic errors."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when a specified repository cannot be found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit is exceeded."""
