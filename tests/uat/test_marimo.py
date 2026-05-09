from pathlib import Path


def test_marimo_notebook_exists() -> None:
    """Ensure the UAT notebook exists."""
    assert Path("tests/uat/UAT_AND_TUTORIAL.py").exists()
