class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded."""

class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested GitHub repository is not found."""
