import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import os
    import sys
    from pathlib import Path

    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from datetime import datetime
    from pydantic import ValidationError
    from src.config.settings import AppConfig, get_settings
    from src.domain_models.commit import CommitData
    from src.domain_models.repository import RepositoryInfo

    import marimo as mo
    return AppConfig, CommitData, RepositoryInfo, ValidationError, datetime, get_settings, mo, os, project_root, sys


@app.cell
def __(mo):
    mo.md(
        """
        # UAT Cycle 01: System Setup, Domain Models & Configuration

        This notebook demonstrates the correct functioning of our fundamental setup according to the UAT scenarios.
        """
    )


@app.cell
def __(AppConfig, ValidationError, mo, os):
    mo.md("## Scenario 1: Strict Environment Configuration Verification (UAT-C01-01)")

    # GIVEN the application environment is missing the GITHUB_TOKEN variable
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]

    try:
        AppConfig(_env_file=None)
        missing_token_result = "Failed: Did not raise ValidationError"
    except ValidationError as e:
        missing_token_result = f"Passed: Raised ValidationError as expected.\\n{e}"

    # GIVEN a valid GITHUB_TOKEN exists
    os.environ["GITHUB_TOKEN"] = "valid_dummy_token"
    try:
        config = AppConfig(_env_file=None)
        valid_token_result = f"Passed: AppConfig instantiated with token {config.GITHUB_TOKEN}"
    except Exception as e:
        valid_token_result = f"Failed: {e}"

    # GIVEN an attempt to inject arbitrary extra configuration variables
    try:
        AppConfig(GITHUB_TOKEN="dummy", UNKNOWN_VAR="test", _env_file=None)
        extra_var_result = "Failed: Did not raise ValidationError for extra variable"
    except ValidationError as e:
        if any(err["type"] == "extra_forbidden" for err in e.errors()):
            extra_var_result = "Passed: Raised extra_forbidden ValidationError"
        else:
            extra_var_result = f"Failed: Raised ValidationError but not extra_forbidden.\\n{e}"

    mo.md(
        f"""
        **Results:**
        - Missing Token: {missing_token_result}
        - Valid Token: {valid_token_result}
        - Extra Variable: {extra_var_result}
        """
    )
    return config, extra_var_result, missing_token_result, valid_token_result


@app.cell
def __(CommitData, RepositoryInfo, datetime, mo):
    mo.md("## Scenario 2: Data Schema Flattening and Validation (UAT-C01-02)")

    # GIVEN a massive, complex dictionary representing a raw GitHub Repository API payload
    repo_payload = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 1000,
        "forks_count": 500,
        "open_issues_count": 100,
        "extra_field_1": "ignore me",
        "extra_field_2": {"nested": "ignore me too"},
        "id": 1234567,
    }

    repo_info = RepositoryInfo(**repo_payload)

    repo_result = "Passed" if not hasattr(repo_info, "extra_field_1") and repo_info.stargazers_count == 1000 else "Failed"

    # GIVEN a heavily nested dictionary representing a raw GitHub Commit API payload
    commit_payload = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {
                "name": "John Doe",
                "email": "john@example.com",
                "date": "2023-01-01T12:00:00Z"
            },
            "message": "Initial commit"
        },
        "url": "https://api.github.com/...",
    }

    commit_info = CommitData.model_validate(commit_payload)

    commit_result = "Passed" if commit_info.author_name == "John Doe" and isinstance(commit_info.date, datetime) else "Failed"

    mo.md(
        f"""
        **Results:**
        - Repository Extra Fields Ignored: {repo_result}
        - Commit Nested Data Flattened: {commit_result}
        """
    )
    return commit_info, commit_payload, commit_result, repo_info, repo_payload, repo_result


if __name__ == "__main__":
    app.run()
