import logging

from src.domain_models.dashboard import DashboardData
from src.domain_models.exceptions import GitHubAPIError, RateLimitError, RepositoryNotFoundError
from src.domain_models.github import RepoMetadata
from src.ingestion.github_client import fetch_commits, fetch_repo_metadata
from src.processing.cache_manager import (
    load_from_cache,
    load_metadata_cache,
    save_metadata_cache,
    save_to_cache,
)
from src.processing.transformer import (
    transform_commits_to_daily_trends,
    transform_commits_to_top_committers,
)

logger = logging.getLogger(__name__)


def get_dashboard_data(repo_name: str) -> DashboardData | str:
    """
    Orchestrates the data flow: Cache -> API -> Transformation -> Cache.
    Returns the mapped DashboardData DTO or a safe error string.
    """
    try:
        # Check cache
        daily_commits_df = load_from_cache(f"{repo_name}_daily_commits")
        top_committers_df = load_from_cache(f"{repo_name}_top_committers")

        repo_metadata_dict = load_metadata_cache(f"{repo_name}_metadata")

        if daily_commits_df is None or top_committers_df is None or repo_metadata_dict is None:
            # Cache miss, fetch and transform
            repo_metadata = fetch_repo_metadata(repo_name)
            commits = fetch_commits(repo_name, limit=100)
            daily_commits_df = transform_commits_to_daily_trends(commits)
            top_committers_df = transform_commits_to_top_committers(commits)

            # Save to cache
            save_to_cache(f"{repo_name}_daily_commits", daily_commits_df)
            save_to_cache(f"{repo_name}_top_committers", top_committers_df)
            save_metadata_cache(f"{repo_name}_metadata", repo_metadata.model_dump())
        else:
            repo_metadata = RepoMetadata(**repo_metadata_dict)

        return DashboardData(
            repo_metadata=repo_metadata,
            daily_commits_df=daily_commits_df,
            top_committers_df=top_committers_df,
        )

    except RepositoryNotFoundError:
        return "Repository not found. Please check the owner/repo spelling."
    except RateLimitError:
        return "GitHub API rate limit exceeded. Please try again later."
    except GitHubAPIError:
        logger.exception("GitHub API Error")
        return "An unexpected error occurred while communicating with GitHub."
    except Exception:
        logger.exception("Unexpected system error")
        return "An unexpected system error occurred."
