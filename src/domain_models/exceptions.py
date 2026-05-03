class DomainError(Exception):
    """Base class for all domain errors."""


class AuthenticationError(DomainError):
    """Raised when authentication fails (e.g., invalid token)."""


class RepositoryNotFoundError(DomainError):
    """Raised when a specified repository cannot be found."""


class RateLimitError(DomainError):
    """Raised when the API rate limit is exceeded."""


class GitHubAPIError(DomainError):
    """Raised for general GitHub API errors."""
