import logging
from collections.abc import Callable

from src.domain_models import CommitRecord, DashboardData, DomainError, RepositoryMetadata
from src.processing.cache_manager import load_from_cache, save_to_cache
from src.processing.transformer import calculate_daily_commits, get_top_committers

logger = logging.getLogger(__name__)


def get_dashboard_data(
    repo_name: str,
    fetch_metadata_func: Callable[[str], RepositoryMetadata],
    fetch_commits_func: Callable[[str], list[CommitRecord]],
) -> DashboardData | str:
    """
    Orchestrates the retrieval and processing of repository data for the dashboard.
    Acts as an anti-corruption layer, returning a string message if a DomainError occurs.
    """
    try:
        # Fetch metadata first
        metadata = fetch_metadata_func(repo_name)

        # Check cache for processed DataFrames
        cached_daily_df = load_from_cache(f"{repo_name}_daily")
        cached_top_df = load_from_cache(f"{repo_name}_top")

        if cached_daily_df is not None and cached_top_df is not None:
            return DashboardData(
                repo_metadata=metadata,
                daily_commits_df=cached_daily_df,
                top_committers_df=cached_top_df,
            )

        # If cache miss, fetch from API and process
        records = fetch_commits_func(repo_name)

        daily_df = calculate_daily_commits(records)
        top_df = get_top_committers(records)

        # Save to cache for subsequent requests
        save_to_cache(f"{repo_name}_daily", daily_df)
        save_to_cache(f"{repo_name}_top", top_df)

        return DashboardData(
            repo_metadata=metadata,
            daily_commits_df=daily_df,
            top_committers_df=top_df,
        )

    except DomainError as e:
        logger.warning(f"DomainError encountered while processing {repo_name}: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"Unexpected error processing {repo_name}: {e}", exc_info=True)
        return "An unexpected error occurred while fetching dashboard data."
