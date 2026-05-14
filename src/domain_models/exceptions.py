class GitHubAnalyticsError(Exception):
    """Base exception for all GitHub Analytics related errors."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when a specified repository cannot be found on GitHub."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when the GitHub API rate limit has been exceeded."""
