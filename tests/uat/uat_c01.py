import json
import os
from datetime import datetime

from pydantic import ValidationError

from src.config import Settings
from src.domain_models.schemas import CommitItem


def run_uat_c01_01() -> None:
    print("Running UAT-C01-01: Environment Configuration Enforcement")  # noqa: T201

    # GIVEN the application environment is completely clear of any GitHub tokens
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]

    # WHEN the system attempts to initialize the configuration settings
    try:
        Settings()  # type: ignore[call-arg]
    except ValidationError as e:
        # THEN the system must immediately raise a validation exception
        print("✓ Validation exception raised successfully.")  # noqa: T201
        # AND the error message must clearly state that GITHUB_TOKEN is missing.
        error_msg = str(e)
        assert "GITHUB_TOKEN" in error_msg, "Error message does not mention GITHUB_TOKEN"
        print("✓ Error message mentions GITHUB_TOKEN.")  # noqa: T201
    else:
        err_msg = "Expected ValidationError was not raised"
        raise AssertionError(err_msg)


def run_uat_c01_02() -> None:
    print("\nRunning UAT-C01-02: Domain Model Validation")  # noqa: T201

    # GIVEN a JSON string representing a valid GitHub commit payload with nested author and date fields
    valid_payload_str = json.dumps(
        {
            "commit": {
                "author": {
                    "name": "Jane Doe",
                    "date": "2023-10-27T10:00:00Z",
                    "email": "jane@example.com",
                },
                "message": "Update README",
            },
            "sha": "abcdef123",
        }
    )

    # WHEN the data is passed to the CommitItem domain model
    data = json.loads(valid_payload_str)
    model = CommitItem(**data)

    # THEN the model must successfully parse the data
    print("✓ Model parsed data successfully.")  # noqa: T201

    # AND the date string must be converted into a native Python datetime object
    assert isinstance(model.commit.author.date, datetime)
    print("✓ Date successfully converted to native Python datetime object.")  # noqa: T201

    # AND if a required field is missing, a validation error must be raised.
    invalid_payload_str = json.dumps({"commit": {"author": {"date": "2023-10-27T10:00:00Z"}}})
    invalid_data = json.loads(invalid_payload_str)

    try:
        CommitItem(**invalid_data)
    except ValidationError:
        print("✓ Validation error raised for missing required field.")  # noqa: T201
    else:
        err_msg = "Expected ValidationError for missing field was not raised"
        raise AssertionError(err_msg)


if __name__ == "__main__":
    run_uat_c01_01()
    run_uat_c01_02()
    print("\nAll UAT scenarios passed!")  # noqa: T201
