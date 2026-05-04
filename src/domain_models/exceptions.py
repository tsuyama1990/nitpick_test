class DomainError(Exception):
    """Base class for all domain-specific exceptions."""


class AuthenticationError(DomainError):
    """Raised when authentication fails (e.g., HTTP 401/403 with invalid token)."""


class RateLimitError(DomainError):
    """Raised when the API rate limit is exceeded (e.g., HTTP 429)."""


class RepositoryNotFoundError(DomainError):
    """Raised when the requested repository does not exist (e.g., HTTP 404)."""
