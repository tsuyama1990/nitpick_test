class DomainError(Exception):
    """Base class for all domain-specific exceptions."""


class AuthenticationError(DomainError):
    """Raised when authentication fails (e.g., HTTP 401/403)."""


class RateLimitError(DomainError):
    """Raised when the API rate limit is exceeded (e.g., HTTP 429)."""


class RepositoryNotFoundError(DomainError):
    """Raised when a repository is not found (e.g., HTTP 404)."""
