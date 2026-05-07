from src.config.settings import get_settings
from src.services.github import fetch_repository_data


def main() -> None:
    settings = get_settings()
    repo_info, _ = fetch_repository_data(settings.GITHUB_TOKEN, "streamlit", "streamlit")
    msg = f"Repo {repo_info.name} has {repo_info.stargazers_count} stars."
    print(msg)  # noqa: T201


if __name__ == "__main__":
    main()
