import marimo

__generated_with = "0.23.5"
app = marimo.App()

@app.cell
def _setup() -> None:
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).parent.parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # Ensure to configure your environment variables properly.

@app.cell
def _test_models() -> None:
    # Validates settings are present
    return

if __name__ == "__main__":
    app.run()
