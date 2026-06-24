class GitHubAnalyticsError(Exception):
    """Base exception class for GitHub Analytics application."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Exception raised when a repository is not found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Exception raised when the GitHub API rate limit is exceeded."""
