import os
from unittest import mock

from pydantic import ValidationError

from src.domain_models import CommitItem, Settings


def test_uat_c01_01() -> None:
    """
    UAT-C01-01: Environment Configuration Enforcement
    GIVEN the application environment is completely clear of any GitHub tokens
    WHEN the system attempts to initialize the configuration settings
    THEN the system must immediately raise a validation exception, halting execution
    AND the error message must clearly state that GITHUB_TOKEN is missing.
    """
    with mock.patch.dict(os.environ, {"ENV_FILE": ".env.fake"}, clear=True):
        try:
            Settings()  # type: ignore[call-arg]
            err_msg = "Settings should have raised ValidationError for missing GITHUB_TOKEN"
            raise AssertionError(err_msg)
        except ValidationError as e:
            if "GITHUB_TOKEN" not in str(e):
                err_msg = "Expected GITHUB_TOKEN in validation error message"
                raise AssertionError(err_msg) from e


def test_uat_c01_02() -> None:
    """
    UAT-C01-02: Domain Model Validation
    GIVEN a JSON string representing a valid GitHub commit payload with nested author and date fields
    WHEN the data is passed to the CommitItem domain model
    THEN the model must successfully parse the data
    AND the date string must be converted into a native Python datetime object
    AND if a required field is missing, a validation error must be raised.
    """
    payload = {
        "commit": {
            "author": {"name": "Test User", "date": "2023-01-01T12:00:00Z"},
            "message": "Update code",
        },
        "sha": "abcdef123456",
    }

    # 1. Successfully parse data and 2. Convert date string to datetime
    item = CommitItem(**payload)  # type: ignore[arg-type]
    assert item.commit.author.name == "Test User"
    assert item.commit.author.date.isoformat() == "2023-01-01T12:00:00+00:00"

    # 3. Missing required field raises validation error
    invalid_payload = {
        "commit": {
            "author": {"date": "2023-01-01T12:00:00Z"},  # Missing name
        }
    }
    try:
        CommitItem(**invalid_payload)  # type: ignore[arg-type]
        err_msg = "CommitItem should have raised ValidationError for missing author name"
        raise AssertionError(err_msg)
    except ValidationError:
        pass


if __name__ == "__main__":
    test_uat_c01_01()
    test_uat_c01_02()

# Added explicitly to avoid Ruff overwriting and errors in earlier run.
