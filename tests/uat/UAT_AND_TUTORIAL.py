import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent.parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pydantic import ValidationError  # noqa: E402

from src.domain_models import CommitItem, Settings, get_settings  # noqa: E402


def uat_c01_01_environment_configuration_enforcement() -> None:
    """
    UAT-C01-01: Environment Configuration Enforcement
    GIVEN the application environment is completely clear of any GitHub tokens
    WHEN the system attempts to initialize the configuration settings
    THEN the system must immediately raise a validation exception, halting execution
    AND the error message must clearly state that GITHUB_TOKEN is missing.
    """
    print("Running UAT-C01-01: Environment Configuration Enforcement...")

    # Clear environment variables
    original_token = os.environ.get("GITHUB_TOKEN")
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    get_settings.cache_clear()

    try:
        # Attempt to initialize
        Settings()  # type: ignore[call-arg]
    except ValidationError as e:
        print("✓ Successfully raised ValidationError for missing GITHUB_TOKEN.")
        assert "GITHUB_TOKEN" in str(e)
    else:
        msg = "Expected ValidationError was not raised."
        raise AssertionError(msg)
    finally:
        # Restore environment variables
        if original_token is not None:
            os.environ["GITHUB_TOKEN"] = original_token


def uat_c01_02_domain_model_validation() -> None:
    """
    UAT-C01-02: Domain Model Validation
    GIVEN a JSON string representing a valid GitHub commit payload with nested author and date fields
    WHEN the data is passed to the CommitItem domain model
    THEN the model must successfully parse the data
    AND the date string must be converted into a native Python datetime object
    AND if a required field is missing, a validation error must be raised.
    """
    print("Running UAT-C01-02: Domain Model Validation...")

    valid_payload = {"commit": {"author": {"name": "Octocat", "date": "2023-10-25T15:30:00Z"}}}

    # Successful parse
    item = CommitItem(**valid_payload)  # type: ignore[arg-type]
    print(
        f"✓ Parsed valid payload successfully. Author: {item.commit.author.name}, Date: {item.commit.author.date}"
    )

    # Missing required field
    invalid_payload = {"commit": {"author": {"date": "2023-10-25T15:30:00Z"}}}
    try:
        CommitItem(**invalid_payload)  # type: ignore[arg-type]
    except ValidationError:
        print("✓ Successfully raised ValidationError for missing required field.")
    else:
        msg = "Expected ValidationError for missing required field was not raised."
        raise AssertionError(msg)


def run_all() -> None:
    print("Starting User Acceptance Testing for Cycle 01...\n")
    uat_c01_01_environment_configuration_enforcement()
    print("-" * 50)
    uat_c01_02_domain_model_validation()
    print("\n✓ All UAT scenarios completed successfully.")


if __name__ == "__main__":
    run_all()
