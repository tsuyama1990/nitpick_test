import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_API_BASE_URL = os.environ.get("GITHUB_API_BASE_URL", "https://api.github.com")

try:
    GITHUB_API_TIMEOUT = float(os.environ.get("GITHUB_API_TIMEOUT", "10.0"))
    if GITHUB_API_TIMEOUT <= 0:
        GITHUB_API_TIMEOUT = 10.0
except ValueError:
    GITHUB_API_TIMEOUT = 10.0


def get_github_token() -> str:
    """
    Retrieves the GitHub Personal Access Token from the environment.
    Raises a ValueError if the token is not found or is empty.
    """
    token: str | None = os.environ.get("GITHUB_TOKEN")
    if not token or not token.strip():
        msg = "GITHUB_TOKEN environment variable is not set or empty."
        raise ValueError(msg)
    return token.strip()
