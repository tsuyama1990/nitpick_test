import marimo

__generated_with = "0.23.5"
app = marimo.App()

@app.cell
def __():
    import marimo as mo
    return (mo,)

@app.cell
def __(mo):
    mo.md(
        """
        # UAT: GitHub Dashboard UI Validation

        This notebook serves as the final validation layer for Cycle 03. Since testing Streamlit directly via standard Pytest tools is fragile, this interactive tutorial walks the tester through manual User Acceptance Testing procedures.

        ### E2E Test Strategy
        1. Run `uv run streamlit run src/presentation/app.py`.
        2. Enter a valid repository (e.g., `streamlit/streamlit` or `tiangolo/fastapi`).
        3. Observe the KPIs and charts rendering correctly.
        4. Enter an invalid repository (e.g., `invalid/repo`).
        5. Observe the graceful error banner.
        """
    )

if __name__ == "__main__":
    app.run()
