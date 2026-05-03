import streamlit as st

from src.domain_models import CommitRecord, DashboardData, RepositoryMetadata
from src.presentation.controller import get_dashboard_data


# NOTE: Since the real GitHub API client is not fully available in this branch,
# we define a dummy client here. In a real integration, this would be imported
# from src.ingestion.github_client
def mock_fetch_metadata(repo_name: str) -> RepositoryMetadata:
    if repo_name == "invalid-owner/repo12345":
        from src.domain_models import RepositoryNotFoundError

        msg = "The specified repository was not found."
        raise RepositoryNotFoundError(msg)

    return RepositoryMetadata(
        owner=repo_name.split("/", maxsplit=1)[0],
        name=repo_name.split("/")[1] if "/" in repo_name else repo_name,
        star_count=100,
        fork_count=50,
        open_issue_count=10,
    )


def mock_fetch_commits(repo_name: str) -> list[CommitRecord]:
    import secrets
    from datetime import UTC, datetime, timedelta

    records = []
    base_date = datetime.now(tz=UTC)
    authors = ["alice", "bob", "charlie", "dave"]

    for i in range(100):
        records.append(
            CommitRecord(
                commit_hash=f"hash{i}",
                author=secrets.choice(authors),
                date=base_date - timedelta(days=secrets.randbelow(11)),
            )
        )
    return records


st.set_page_config(page_title="GitHub Repository Analysis Dashboard", layout="wide")

st.title("GitHub Repository Analysis Dashboard")
st.write(
    "Enter a GitHub repository name (e.g., `streamlit/streamlit`) to view key metrics and commit activity."
)

repo_name = st.text_input("Repository Name", placeholder="owner/repo")

if repo_name:
    with st.spinner(f"Fetching data for {repo_name}..."):
        result = get_dashboard_data(repo_name, mock_fetch_metadata, mock_fetch_commits)

        if isinstance(result, str):
            st.error(result)
        elif isinstance(result, DashboardData):
            st.subheader(f"Metrics for {result.repo_metadata.owner}/{result.repo_metadata.name}")

            # KPI Layout
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Stars", result.repo_metadata.star_count)
            col2.metric("Total Forks", result.repo_metadata.fork_count)
            col3.metric("Open Issues", result.repo_metadata.open_issue_count)

            st.divider()

            st.subheader("Daily Commits")
            if not result.daily_commits_df.is_empty():
                # Convert to pandas for Streamlit if necessary, though newer streamlit might support polars
                daily_pd = result.daily_commits_df.to_pandas()
                st.line_chart(daily_pd, x="date", y="commit_count")
            else:
                st.info("No commit data available.")

            st.subheader("Top 5 Committers")
            if not result.top_committers_df.is_empty():
                top_pd = result.top_committers_df.to_pandas()
                st.bar_chart(top_pd, x="author", y="commit_count")
            else:
                st.info("No committer data available.")
