# ruff: noqa: F841, T201
from src.domain_models.config import get_settings
from src.ingestion.github_client import GitHubClient


def main() -> None:
    settings = get_settings()
    client = GitHubClient(token=settings.GITHUB_TOKEN)
    print("GitHub client initialized successfully.")

if __name__ == "__main__":
    main()
