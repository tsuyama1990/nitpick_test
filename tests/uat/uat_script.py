import os
import sys
import unittest.mock
from typing import Any

from pydantic import ValidationError

from src.config import Settings
from src.domain_models.schemas import CommitItem


# UAT-C01-01
def test_missing_github_token() -> None:
    print("Running UAT-C01-01: Environment Configuration Enforcement")  # noqa: T201
    with unittest.mock.patch.dict(os.environ, {}, clear=True):
        try:
            Settings()  # type: ignore[call-arg]
            print("FAILED: Expected ValidationError due to missing token")  # noqa: T201
            sys.exit(1)
        except ValidationError as e:
            if "GITHUB_TOKEN" in str(e):
                print("PASSED: Successfully rejected configuration due to missing GITHUB_TOKEN")  # noqa: T201
            else:
                print(f"FAILED: Exception raised but didn't mention GITHUB_TOKEN. {e}")  # noqa: T201
                sys.exit(1)


# UAT-C01-02
def test_domain_model_validation() -> None:
    print("Running UAT-C01-02: Domain Model Validation")  # noqa: T201
    valid_payload: dict[str, Any] = {"commit": {"author": {"name": "Jane Doe", "date": "2023-11-01T12:00:00Z"}}}

    item = CommitItem(**valid_payload)
    if item.commit.author.name == "Jane Doe" and item.commit.author.date.year == 2023:
        print("PASSED: Correctly parsed valid payload")  # noqa: T201
    else:
        print("FAILED: Failed to parse valid payload")  # noqa: T201
        sys.exit(1)

    invalid_payload: dict[str, Any] = {"commit": {"author": {"date": "2023-11-01T12:00:00Z"}}}
    try:
        CommitItem(**invalid_payload)
        print("FAILED: Expected ValidationError due to missing name")  # noqa: T201
        sys.exit(1)
    except ValidationError:
        print("PASSED: Successfully rejected invalid payload")  # noqa: T201


if __name__ == "__main__":
    test_missing_github_token()
    test_domain_model_validation()
