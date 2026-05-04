def main() -> None:
    from src.config import get_settings
    from src.ingestion.github_client import GitHubClient

    token = get_settings().GITHUB_TOKEN
    client = GitHubClient(token=token)
    repo = client.fetch_repository_metadata("streamlit", "streamlit")
    print(f"{repo.owner}/{repo.name}: ⭐{repo.stargazers_count} 🍴{repo.forks_count}")  # noqa: T201


if __name__ == "__main__":
    main()
