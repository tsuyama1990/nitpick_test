class DomainError(Exception):
    """Base class for all domain exceptions."""


class AuthenticationError(DomainError):
    """Raised when authentication with the external API fails."""


class RateLimitError(DomainError):
    """Raised when the external API rate limit is exceeded."""


class RepositoryNotFoundError(DomainError):
    """Raised when the requested repository is not found."""
