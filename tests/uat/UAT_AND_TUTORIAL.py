import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import sys
    from pathlib import Path

    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)

    import os
    from unittest.mock import patch

    import polars as pl
    import pytest

    from src.domain_models.github import CommitInfo, RepoInfo
    from src.services.dashboard_controller import DashboardController
    from src.services.exceptions import DashboardError

    return DashboardController, RepoInfo, CommitInfo, DashboardError, pl, patch, os, pytest


@app.cell
def __(DashboardController, RepoInfo, CommitInfo, DashboardError, pl, patch, os, pytest):
    # Mock Mode Configuration
    os.environ["GITHUB_TOKEN"] = "mock_token"

    # Simple Mock Tests for the UAT scenario
    def run_mocked_uat_scenario_1() -> None:
        """Scenario 1: Full cycle and cache behavior."""
        with (
            patch("src.ingestion.client.GitHubClient.get_repo_info") as mock_repo,
            patch("src.ingestion.client.GitHubClient.get_recent_commits") as mock_commits,
        ):
            mock_repo.return_value = RepoInfo(
                stargazers_count=1000, forks_count=100, open_issues_count=10
            )
            mock_commits.return_value = []

            controller = DashboardController()

            # Fetch once
            res1 = controller.get_dashboard_data("test/repo")
            assert res1.cached is False

            # Fetch twice (should hit cache for commits)
            res2 = controller.get_dashboard_data("test/repo")
            assert res2.cached is True

    run_mocked_uat_scenario_1()

    def run_mocked_uat_scenario_2() -> None:
        """Scenario 2: Negative Flow Error Handling."""
        with patch(
            "src.ingestion.client.GitHubClient.get_repo_info", side_effect=Exception("API Error")
        ):
            controller = DashboardController()
            with pytest.raises(DashboardError):
                controller.get_dashboard_data("test/repo")

    run_mocked_uat_scenario_2()

    print("All mock UAT scenarios passed successfully!")
    return run_mocked_uat_scenario_1, run_mocked_uat_scenario_2


if __name__ == "__main__":
    app.run()
