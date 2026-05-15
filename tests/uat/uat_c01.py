import os

# Ensure imports work when running as a standalone script
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from pydantic import ValidationError

from src.domain_models.config import Settings
from src.domain_models.schemas import CommitItem


def test_uat_c01_01_environment_enforcement() -> None:
    """
    UAT-C01-01: Verify the application enforces the presence of the GITHUB_TOKEN environment variable.
    """
    print("Running UAT-C01-01: Environment Configuration Enforcement")

    # GIVEN the application environment is completely clear of any GitHub tokens
    env = os.environ.copy()
    if "GITHUB_TOKEN" in env:
        del env["GITHUB_TOKEN"]

    # WHEN the system attempts to initialize the configuration settings
    try:
        # Avoid relying on pydantic loading the .env file with existing tokens during the test
        os.environ.clear()
        os.environ.update(env)
        # Suppress dotenv to ensure clean environment test
        Settings(_env_file=None)  # type: ignore[call-arg]

        # If it reaches here, the test failed
        print("❌ FAILED: Settings loaded without GITHUB_TOKEN")
        sys.exit(1)

    except ValidationError as e:
        # THEN the system must immediately raise a validation exception
        # AND the error message must clearly state that GITHUB_TOKEN is missing
        if "GITHUB_TOKEN" in str(e) or "github_token" in str(e).lower():
            print("✅ PASSED: GITHUB_TOKEN is strictly required.")
        else:
            print(
                f"❌ FAILED: Validation error raised but does not mention GITHUB_TOKEN. Error: {e}"
            )
            sys.exit(1)


def test_uat_c01_02_domain_model_validation() -> None:
    """
    UAT-C01-02: Verify the Pydantic domain models correctly parse mock JSON payloads representing GitHub API responses.
    """
    print("\nRunning UAT-C01-02: Domain Model Validation")

    # GIVEN a JSON string representing a valid GitHub commit payload
    valid_payload = {
        "sha": "d41d8cd98f00b204e9800998ecf8427e",
        "commit": {
            "author": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "date": "2023-11-01T12:34:56Z",
            },
            "committer": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "date": "2023-11-01T12:34:56Z",
            },
            "message": "Update README.md",
        },
    }

    # WHEN the data is passed to the CommitItem domain model
    # THEN the model must successfully parse the data
    try:
        model = CommitItem(**valid_payload)  # type: ignore[arg-type]

        # AND the date string must be converted into a native Python datetime object
        assert model.commit.author.date.year == 2023, "Date not correctly parsed to datetime"
        assert model.commit.author.name == "Jane Doe", "Name not correctly parsed"

        # Test missing field behavior
        invalid_payload = {"commit": {"author": {"date": "2023-11-01T12:34:56Z"}}}

        try:
            CommitItem(**invalid_payload)  # type: ignore[arg-type]
            print("❌ FAILED: Did not raise ValidationError on missing 'name' field")
            sys.exit(1)
        except ValidationError:
            # AND if a required field is missing, a validation error must be raised
            print("✅ PASSED: Successfully parsed valid payload and rejected invalid payload.")

    except Exception as e:
        print(f"❌ FAILED: Unexpected error during parsing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_uat_c01_01_environment_enforcement()
    test_uat_c01_02_domain_model_validation()
    print("\n🎉 All UAT scenarios passed!")
