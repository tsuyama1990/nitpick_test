class GitHubAnalyticsError(Exception):
    """Base exception for GitHub Analytics."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Raised when the repository is not found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Raised when GitHub API rate limit is exceeded."""
