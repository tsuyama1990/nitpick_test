import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md("# UAT Scenario C01-01")


@app.cell
def __():
    # Will be implemented
    return


if __name__ == "__main__":
    app.run()
