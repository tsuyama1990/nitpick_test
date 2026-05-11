import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent.resolve())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return (project_root,)


@app.cell
def __(project_root):
    import os

    from pydantic import ValidationError

    from src.domain_models.config import Settings, get_settings
    from src.domain_models.schemas import CommitItem

    print("Executing UAT-C01-01: Environment Configuration Enforcement")

    # Store original and clear
    original_token = os.environ.get("GITHUB_TOKEN")
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    get_settings.cache_clear()

    try:
        Settings()
        msg = "Should have raised ValidationError"
        raise AssertionError(msg)
    except ValidationError as e:
        assert "GITHUB_TOKEN" in str(e)
        print("✓ UAT-C01-01 Passed: Configuration correctly enforced GITHUB_TOKEN presence.")

    # Restore original if present for future cells
    if original_token is not None:
        os.environ["GITHUB_TOKEN"] = original_token

    print("\nExecuting UAT-C01-02: Domain Model Validation")
    mock_payload = {
        "sha": "123",
        "commit": {
            "author": {
                "name": "Test Author",
                "date": "2023-12-01T12:00:00Z",
                "email": "test@example.com",
            },
            "message": "test message",
        },
    }

    commit_item = CommitItem(**mock_payload)
    assert commit_item.commit.author.name == "Test Author"
    from datetime import UTC, datetime

    assert commit_item.commit.author.date == datetime(2023, 12, 1, 12, 0, tzinfo=UTC)

    try:
        CommitItem(commit={"author": {"date": "invalid"}})
        msg = "Should have raised ValidationError"
        raise AssertionError(msg)
    except ValidationError:
        pass

    print("✓ UAT-C01-02 Passed: Domain Model correctly validated data and parsed dates.")
    return CommitItem, Settings, ValidationError, get_settings, mock_payload, original_token


if __name__ == "__main__":
    app.run()
