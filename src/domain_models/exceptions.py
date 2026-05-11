class GitHubAnalyticsError(Exception):
    """Base exception for all GitHub Analytics related errors."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when the requested GitHub repository cannot be found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit is exceeded."""
