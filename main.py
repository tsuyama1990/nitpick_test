from src.domain_models.config import get_settings
from src.ingestion.github_client import GitHubClient


def main() -> None:
    settings = get_settings()
    client = GitHubClient(token=settings.GITHUB_TOKEN)  # noqa: F841
    print("GitHub client initialized successfully.")  # noqa: T201


if __name__ == "__main__":
    main()
