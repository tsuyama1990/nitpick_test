import os

from dotenv import load_dotenv

load_dotenv()


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
