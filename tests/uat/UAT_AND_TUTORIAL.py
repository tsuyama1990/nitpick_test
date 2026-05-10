import os
import sys
from datetime import UTC

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    sys.path.append(".")
    return sys,


@app.cell
def __(sys):
    from unittest.mock import patch

    from pydantic import ValidationError

    from src.config import Settings, get_settings
    from src.domain_models.schemas import CommitItem, RepositoryMetrics

    print("Importing domain models and config...")
    return CommitItem, RepositoryMetrics, Settings, ValidationError, get_settings, os, patch


@app.cell
def __(Settings, ValidationError, get_settings, os, patch):
    print("--- UAT-C01-01: Environment Configuration Enforcement ---")

    # GIVEN the application environment is completely clear of any GitHub tokens
    with patch.dict(os.environ, {}, clear=True):
        try:
            # WHEN the system attempts to initialize the configuration settings
            get_settings.cache_clear()
            Settings()
            print("ERROR: Should have raised ValidationError")
        except ValidationError as e:
            # THEN the system must immediately raise a validation exception, halting execution
            # AND the error message must clearly state that GITHUB_TOKEN is missing.
            if "GITHUB_TOKEN" in str(e):
                print("SUCCESS: System correctly raised validation exception for missing GITHUB_TOKEN")
            else:
                print("ERROR: Validation exception raised but did not specify GITHUB_TOKEN missing")


@app.cell
def __(CommitItem, ValidationError):
    print("--- UAT-C01-02: Domain Model Validation ---")

    # GIVEN a JSON string representing a valid GitHub commit payload with nested author and date fields
    valid_payload = {
        "commit": {
            "author": {
                "name": "Octocat",
                "date": "2024-05-10T12:00:00Z",
                "email": "octocat@github.com"
            },
            "message": "Initial commit"
        },
        "url": "https://api.github.com/repos/octocat/Hello-World/commits/sha"
    }

    # WHEN the data is passed to the CommitItem domain model
    item = CommitItem(**valid_payload)

    # THEN the model must successfully parse the data
    # AND the date string must be converted into a native Python datetime object
    from datetime import datetime
    expected_date = datetime(2024, 5, 10, 12, 0, 0, tzinfo=UTC)
    if item.commit.author.date == expected_date:
        print(f"SUCCESS: Date parsed correctly into native object: {item.commit.author.date}")
    else:
        print("ERROR: Date was not parsed correctly")

    # AND if a required field is missing, a validation error must be raised.
    invalid_payload = {
        "commit": {
            "author": {
                "date": "2024-05-10T12:00:00Z"
            }
        }
    }
    try:
        CommitItem(**invalid_payload)
        print("ERROR: Should have raised ValidationError for missing required field")
    except ValidationError:
        print("SUCCESS: Validation error correctly raised for missing required field (name).")


if __name__ == "__main__":
    app.run()
