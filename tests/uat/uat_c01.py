"""User Acceptance Testing for Cycle 01."""

import os
from unittest.mock import patch

from pydantic import ValidationError

from src.domain_models import CommitItem, Settings, get_settings


def verify_uat_c01_01() -> None:
    """Verify application enforces GITHUB_TOKEN presence (UAT-C01-01)."""
    print("Running UAT-C01-01: Environment Configuration Enforcement")  # noqa: T201
    get_settings.cache_clear()

    with patch.dict(os.environ, {}, clear=True):
        try:
            Settings()  # type: ignore[call-arg]
            err_msg_missing = "Expected ValidationError was not raised."
            raise AssertionError(err_msg_missing)
        except ValidationError as e:
            error_msg = str(e)
            if "GITHUB_TOKEN" not in error_msg:
                err_msg_no_token = f"Error message does not mention GITHUB_TOKEN: {error_msg}"
                raise AssertionError(err_msg_no_token) from e
            print("✓ System successfully caught missing GITHUB_TOKEN.")  # noqa: T201


def verify_uat_c01_02() -> None:
    """Verify parsing and validation of GitHub commit data (UAT-C01-02)."""
    print("Running UAT-C01-02: Domain Model Validation")  # noqa: T201

    # Valid payload test
    valid_payload: dict[str, object] = {
        "commit": {"author": {"name": "Octocat", "date": "2023-10-25T10:00:00Z"}}
    }
    try:
        model = CommitItem(**valid_payload)  # type: ignore[arg-type]
        print(f"✓ Successfully parsed valid payload. Date: {model.commit.author.date}")  # noqa: T201
    except ValidationError as e:
        err_msg_failed_parse = f"Failed to parse valid payload: {e}"
        raise AssertionError(err_msg_failed_parse) from e

    # Invalid payload test
    invalid_payload: dict[str, object] = {"commit": {"author": {"date": "2023-10-25T10:00:00Z"}}}
    try:
        CommitItem(**invalid_payload)  # type: ignore[arg-type]
        err_msg_expected = "Expected ValidationError was not raised for missing name."
        raise AssertionError(err_msg_expected)
    except ValidationError:
        print("✓ Successfully rejected invalid payload missing required field.")  # noqa: T201


if __name__ == "__main__":
    print("Starting User Acceptance Tests for Cycle 01...")  # noqa: T201
    verify_uat_c01_01()
    verify_uat_c01_02()
    print("All Cycle 01 UATs passed successfully.")  # noqa: T201
