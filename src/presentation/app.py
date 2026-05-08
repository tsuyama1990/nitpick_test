import streamlit as st
from pydantic import ValidationError

from src.ingestion.github_client import get_commits, get_repo_info
from src.transformation.processor import (
    aggregate_commits_per_day,
    get_top_committers,
    load_from_cache,
    save_to_cache,
)


def main() -> None:
    st.title("GitHub Repository Analytics Dashboard")
    st.write(
        "This PoC dashboard displays basic metrics and commit trends for a given GitHub repository."
    )

    repo_input = st.text_input("Enter Repository (owner/repo)", value="streamlit/streamlit")

    if st.button("Fetch Data"):
        if "/" not in repo_input or len(repo_input.split("/")) != 2:
            st.warning("Please enter in 'owner/repo' format.")
            return

        owner, repo = repo_input.split("/")

        try:
            with st.spinner("Fetching data..."):
                repo_info = get_repo_info(owner, repo)

                st.subheader("Repository Metrics")
                col1, col2, col3 = st.columns(3)
                col1.metric("Stars", repo_info.stargazers_count)
                col2.metric("Forks", repo_info.forks_count)
                col3.metric("Open Issues", repo_info.open_issues_count)

                commits_cache_key = f"{owner}_{repo}_commits.parquet"
                top_cache_key = f"{owner}_{repo}_top.parquet"

                df_commits_day = load_from_cache(commits_cache_key)
                df_top_committers = load_from_cache(top_cache_key)

                if df_commits_day is None or df_top_committers is None:
                    commits = get_commits(owner, repo)
                    df_commits_day = aggregate_commits_per_day(commits)
                    df_top_committers = get_top_committers(commits)

                    save_to_cache(df_commits_day, commits_cache_key)
                    save_to_cache(df_top_committers, top_cache_key)
                else:
                    st.info("Loaded data from cache")

                st.subheader("Commits per Day (Last 100)")
                # Convert to pandas for Streamlit native charts
                st.line_chart(df_commits_day.to_pandas().set_index("date")["commit_count"])

                st.subheader("Top 5 Committers")
                st.bar_chart(df_top_committers.to_pandas().set_index("name")["commit_count"])

        except RuntimeError as e:
            if "403" in str(e) or "429" in str(e):
                st.error("Authentication error or rate limit exceeded. Please check your token.")
            elif "404" in str(e):
                st.error("Repository not found. Please check the owner and repo name.")
            else:
                st.error(f"Failed to fetch data: {e}")
        except ValidationError:
            st.error("Configuration error. Check your environment variables.")
        except Exception:
            st.error("An unexpected error occurred.")


if __name__ == "__main__":
    main()
