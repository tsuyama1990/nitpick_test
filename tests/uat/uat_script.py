"""User Acceptance Testing script for Cycle 01."""

import os
from datetime import datetime

import pytest
from pydantic import ValidationError

from src.config import Settings
from src.domain_models.schemas import CommitItem


def test_uat_c01_01_environment_configuration() -> None:
    """UAT-C01-01: Verify the application enforces the presence of GITHUB_TOKEN."""
    print("Running UAT-C01-01: Environment Configuration Enforcement...")  # noqa: T201
    original_token = os.environ.get("GITHUB_TOKEN")

    # GIVEN the application environment is completely clear of any GitHub tokens
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]

    try:
        # WHEN the system attempts to initialize the configuration settings
        with pytest.raises(ValidationError, match="GITHUB_TOKEN"):
            Settings()  # type: ignore[call-arg]
        print("  ✓ Passed: System raised ValidationError when GITHUB_TOKEN was missing.")  # noqa: T201
    finally:
        if original_token is not None:
            os.environ["GITHUB_TOKEN"] = original_token


def test_uat_c01_02_domain_model_validation() -> None:
    """UAT-C01-02: Verify the Pydantic domain models correctly parse mock JSON payloads."""
    print("Running UAT-C01-02: Domain Model Validation...")  # noqa: T201

    # GIVEN a JSON string representing a valid GitHub commit payload with nested author and date fields
    valid_payload: dict[str, object] = {
        "commit": {
            "author": {"name": "Monalisa Octocat", "date": "2023-10-27T10:00:00Z"},
            "message": "Update README",
        },
        "url": "https://api.github.com/repos/...",
    }

    # WHEN the data is passed to the CommitItem domain model
    item = CommitItem(**valid_payload)  # type: ignore[arg-type]

    # THEN the model must successfully parse the data
    assert item.commit.author.name == "Monalisa Octocat"

    # AND the date string must be converted into a native Python datetime object
    assert isinstance(item.commit.author.date, datetime)

    # AND if a required field is missing, a validation error must be raised.
    invalid_payload = {"commit": {"author": {"date": "2023-10-27T10:00:00Z"}}}
    with pytest.raises(ValidationError, match="name"):
        CommitItem(**invalid_payload)  # type: ignore[arg-type]

    print("  ✓ Passed: Model parsed data, converted dates, and raised error for missing fields.")  # noqa: T201


if __name__ == "__main__":
    print("Starting Cycle 01 UAT...")  # noqa: T201
    test_uat_c01_01_environment_configuration()
    test_uat_c01_02_domain_model_validation()
    print("All UATs passed.")  # noqa: T201
