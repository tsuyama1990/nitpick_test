import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def _setup():
    import os
    import sys
    from pathlib import Path

    project_root = str(Path(__file__).parent.parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ["GITHUB_TOKEN"] = "mock_token"


@app.cell
def _test_models():
    from src.domain_models.config import get_settings

    settings = get_settings()
    assert settings.GITHUB_TOKEN == "mock_token"


if __name__ == "__main__":
    app.run()
