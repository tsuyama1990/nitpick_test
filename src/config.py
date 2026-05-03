import os

from dotenv import load_dotenv


def get_github_token() -> str:
    """
    Loads the GITHUB_TOKEN from the environment (.env file).
    Raises an exception if the token is missing or empty.
    """
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    if not token or not token.strip():
        msg = "GITHUB_TOKEN environment variable is not set or is empty."
        raise ValueError(msg)
    return token.strip()
