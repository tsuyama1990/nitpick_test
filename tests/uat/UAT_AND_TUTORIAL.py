import marimo

__generated_with = "0.1.0"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    root = str(Path(__file__).parent.parent.parent)
    if root not in sys.path:
        sys.path.append(root)
    return sys, Path, root


@app.cell
def __(sys, Path, root):
    import os

    from pydantic import ValidationError

    from src.domain_models.config import Settings, get_settings

    print("Running UAT-C01-01...")

    old_token = os.environ.get("GITHUB_TOKEN")
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]

    get_settings.cache_clear()

    try:
        Settings()
        print("FAIL: Expected ValidationError when GITHUB_TOKEN is missing")
        sys.exit(1)
    except ValidationError as e:
        print("SUCCESS: ValidationError raised when GITHUB_TOKEN is missing")
        print(e)

    if old_token is not None:
        os.environ["GITHUB_TOKEN"] = old_token
    return Settings, get_settings, ValidationError, os, old_token


@app.cell
def __(Settings, get_settings, ValidationError, os, sys):
    import datetime
    import json

    from src.domain_models.schemas import CommitItem

    print("Running UAT-C01-02...")

    json_payload = """
    {
        "commit": {
            "author": {
                "name": "Jane Doe",
                "date": "2024-05-20T15:00:00Z",
                "email": "jane@example.com"
            },
            "message": "Initial commit"
        },
        "url": "https://api.github.com/repos/...",
        "sha": "abcdef123456"
    }
    """

    data = json.loads(json_payload)

    try:
        item = CommitItem(**data)
        print("SUCCESS: Parsed CommitItem")
        assert item.commit.author.name == "Jane Doe"
        assert isinstance(item.commit.author.date, datetime.datetime)
        print("SUCCESS: Date is converted to datetime object")
    except ValidationError as e:
        print("FAIL: Validation failed for valid data")
        print(e)
        sys.exit(1)

    json_payload_invalid = """
    {
        "commit": {
            "author": {
                "name": "Jane Doe"
            }
        }
    }
    """
    data_invalid = json.loads(json_payload_invalid)
    try:
        CommitItem(**data_invalid)
        print("FAIL: Expected ValidationError for missing date")
        sys.exit(1)
    except ValidationError as e:
        print("SUCCESS: ValidationError raised for missing required field")
        print(e)

    print("ALL UAT TESTS PASSED")
    return CommitItem, json, datetime, json_payload, data, item, json_payload_invalid, data_invalid


if __name__ == "__main__":
    app.run()
