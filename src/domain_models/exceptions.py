"""Domain exceptions for the application."""


class GitHubAnalyticsError(Exception):
    """Base exception for all GitHub Analytics domain errors."""


class RepositoryNotFoundError(GitHubAnalyticsError):
    """Exception raised when a repository is not found."""


class RateLimitExceededError(GitHubAnalyticsError):
    """Exception raised when the GitHub API rate limit is exceeded."""
