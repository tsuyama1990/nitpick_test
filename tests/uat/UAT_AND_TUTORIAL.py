import marimo

__generated_with = "0.11.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    # Add project root to sys.path to allow imports from src
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)
    return Path, project_root, sys


@app.cell
def _():
    import json
    import os
    from datetime import UTC, datetime

    from pydantic import ValidationError

    from src.domain_models.config import Settings, get_settings
    from src.domain_models.schemas import CommitItem

    return CommitItem, Settings, UTC, ValidationError, datetime, get_settings, json, os


@app.cell
def _(Settings, ValidationError, get_settings, os):
    def test_uat_c01_01():
        """
        UAT-C01-01: Environment Configuration Enforcement
        Verify the application enforces the presence of the GITHUB_TOKEN environment variable.
        """
        print("Running UAT-C01-01: Environment Configuration Enforcement")

        # Clear the cache to ensure we get a fresh read
        get_settings.cache_clear()

        # Save existing token if any
        original_token = os.environ.get("GITHUB_TOKEN")

        try:
            # Simulate environment with missing GITHUB_TOKEN
            if "GITHUB_TOKEN" in os.environ:
                del os.environ["GITHUB_TOKEN"]

            try:
                Settings()
                print(
                    "❌ FAILED: Settings did not raise ValidationError when GITHUB_TOKEN is missing."
                )
            except ValidationError as e:
                print("✅ PASSED: Settings raised ValidationError when GITHUB_TOKEN is missing.")
                assert "GITHUB_TOKEN" in str(e)
        finally:
            # Restore original token
            if original_token is not None:
                os.environ["GITHUB_TOKEN"] = original_token

    return (test_uat_c01_01,)


@app.cell
def _(CommitItem, UTC, ValidationError, datetime, json):
    def test_uat_c01_02():
        """
        UAT-C01-02: Domain Model Validation
        Verify the Pydantic domain models correctly parse mock JSON payloads representing
        GitHub API responses, and strictly validate the data types.
        """
        print("Running UAT-C01-02: Domain Model Validation")

        valid_json = """
        {
            "sha": "d0e1c2",
            "commit": {
                "author": {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "date": "2023-10-27T10:00:00Z"
                },
                "message": "Update README"
            }
        }
        """

        # 1. Parse valid JSON
        data = json.loads(valid_json)
        try:
            item = CommitItem(**data)
            assert item.commit.author.name == "Jane Doe"
            assert item.commit.author.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)
            print("✅ PASSED: Parsed valid JSON payload successfully.")
        except Exception as e:
            print(f"❌ FAILED: Failed to parse valid JSON payload: {e}")

        # 2. Parse invalid JSON (missing required field)
        invalid_json = """
        {
            "commit": {
                "author": {
                    "name": "Jane Doe"
                }
            }
        }
        """
        invalid_data = json.loads(invalid_json)
        try:
            CommitItem(**invalid_data)
            print("❌ FAILED: Did not raise ValidationError on missing date.")
        except ValidationError:
            print("✅ PASSED: Raised ValidationError on missing required field.")

    return (test_uat_c01_02,)


@app.cell
def _(test_uat_c01_01, test_uat_c01_02):
    test_uat_c01_01()
    test_uat_c01_02()
    print("All UAT tests completed.")


if __name__ == "__main__":
    app.run()
