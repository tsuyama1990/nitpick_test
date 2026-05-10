from src.ingestion.client import GitHubAPIError, GitHubClient
from src.services.exceptions import DashboardError
from src.services.models import DashboardResult
from src.storage.cache import CacheManager
from src.transformation.polars_engine import PolarsEngine


class DashboardController:
    """Orchestrates ingestion, transformation, and caching of GitHub data."""

    def __init__(self) -> None:
        self.client = GitHubClient()
        self.cache = CacheManager()

    def _validate_input(self, repo_path: str) -> tuple[str, str]:
        """Validates and splits the owner/repo string."""
        parts = repo_path.strip().split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            msg = "Invalid format. Please use 'owner/repo'."
            raise DashboardError(msg)
        return parts[0], parts[1]

    def get_dashboard_data(self, repo_path: str) -> DashboardResult:
        """
        Retrieves dashboard data, utilizing the cache if valid.

        Args:
            repo_path: The repository path in 'owner/repo' format.

        Returns:
            DashboardResult containing the aggregated data.

        Raises:
            DashboardError: With a user-friendly message if an error occurs.
        """
        try:
            owner, repo = self._validate_input(repo_path)

            # Note: We fetch RepoInfo live every time as it is lightweight
            # and provides real-time KPI metrics.
            repo_info = self.client.get_repo_info(owner, repo)

            cached_commits_by_date = self.cache.load(owner, repo, "commits_by_date")
            cached_top_committers = self.cache.load(owner, repo, "top_committers")

            if cached_commits_by_date is not None and cached_top_committers is not None:
                return DashboardResult(
                    repo_info=repo_info,
                    commits_by_date=cached_commits_by_date,
                    top_committers=cached_top_committers,
                    cached=True,
                )

            # Cache miss -> Fetch fresh data
            commits = self.client.get_recent_commits(owner, repo)

            df_date = PolarsEngine.aggregate_commits_by_date(commits)
            df_top = PolarsEngine.get_top_committers(commits)

            self.cache.save(df_date, owner, repo, "commits_by_date")
            self.cache.save(df_top, owner, repo, "top_committers")

            return DashboardResult(
                repo_info=repo_info, commits_by_date=df_date, top_committers=df_top, cached=False
            )

        except GitHubAPIError as e:
            raise DashboardError(str(e)) from e
        except Exception as e:
            if not isinstance(e, DashboardError):
                msg = f"An unexpected error occurred: {e}"
                raise DashboardError(msg) from e
            raise
