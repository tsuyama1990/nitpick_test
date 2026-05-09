import streamlit as st

from src.clients.github_client import GitHubClientError
from src.services.data_processor import DataProcessor


def main() -> None:
    """Main entrypoint for the Streamlit dashboard."""
    st.title("GitHub Repository Analysis Dashboard")

    repo_input = st.text_input("Enter Repository (owner/repo)", value="")

    if st.button("Analyze"):
        if not repo_input or "/" not in repo_input:
            st.warning("Please enter in 'owner/repo' format.")
            return

        owner, repo = repo_input.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()

        processor = DataProcessor()

        try:
            with st.spinner("Fetching data..."):
                repo_info = processor.get_repo_data(owner, repo)
                df_date, df_user = processor.get_commit_data(owner, repo)

            st.subheader("Repository Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Stars", repo_info.stargazers_count)
            col2.metric("Forks", repo_info.forks_count)
            col3.metric("Open Issues", repo_info.open_issues_count)

            st.subheader("Commits Over Time")
            st.line_chart(df_date, x="date_only", y="commit_count")

            st.subheader("Top 5 Committers")
            st.bar_chart(df_user, x="author_name", y="commit_count")

        except GitHubClientError as e:
            msg = str(e)
            if "Rate limit exceeded or access forbidden" in msg:
                st.error("Authentication error occurred. Please check if the token is valid.")
            elif "Repository not found" in msg:
                st.error("Repository not found. Please check the owner and repo name.")
            else:
                st.error("An error occurred while fetching data from GitHub.")
        except Exception:
            st.error("An unexpected error occurred.")


if __name__ == "__main__":
    main()
