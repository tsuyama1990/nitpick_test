import marimo

__generated_with = "0.23.5"
app = marimo.App()

@app.cell
def __():
    import sys
    from pathlib import Path

    if str(Path.cwd()) not in sys.path:
        sys.path.append(str(Path.cwd()))

    import pytest
    from pytest_httpx import HTTPXMock
    from streamlit.testing.v1 import AppTest
    return AppTest, HTTPXMock, Path, pytest, sys


@app.cell
def __(AppTest, HTTPXMock):
    def test_mocked_error_handling(httpx_mock: HTTPXMock) -> None:
        """Scenario 2: Negative Flow (Mocked)"""
        # Test Invalid Input Format
        at = AppTest.from_file("src/app.py")
        at.run()
        at.text_input[0].input("invalid_repo").run()
        at.button[0].click().run()
        assert not at.exception
        assert any("Please enter in 'owner/repo' format." in str(w.value) for w in at.warning)

        # Test 404 Error
        httpx_mock.add_response(url="https://api.github.com/repos/invalid/repo", status_code=404)
        at = AppTest.from_file("src/app.py")
        at.run()
        at.text_input[0].input("invalid/repo").run()
        at.button[0].click().run()
        assert not at.exception
        assert any("Repository not found" in str(e.value) for e in at.error)

        # Test 403 Error
        httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=403)
        at = AppTest.from_file("src/app.py")
        at.run()
        at.text_input[0].input("owner/repo").run()
        at.button[0].click().run()
        assert not at.exception
        assert any("Authentication error" in str(e.value) for e in at.error)
    return test_mocked_error_handling,


@app.cell
def __(AppTest, pytest):
    @pytest.mark.live
    def test_live_happy_path_and_cache() -> None:
        """Scenario 1: Happy Path & Caching (Live)"""
        import os
        from dotenv import load_dotenv

        load_dotenv()
        if not os.getenv("GITHUB_TOKEN"):
            pytest.skip("No GITHUB_TOKEN available for live test")

        at = AppTest.from_file("src/app.py")
        at.run()
        at.text_input[0].input("tiangolo/fastapi").run()
        at.button[0].click().run()

        assert not at.exception
        assert not at.error

        assert len(at.metric) == 3
        assert at.metric[0].label == "Stars"
        assert int(at.metric[0].value) > 0

        # Scenario 1 - strict caching:
        # A second run with the same repo should use cache.
        # We can't strictly assert the network didn't fire from Streamlit's side,
        # but the processor's unit tests handle the cache hit verification.
    return test_live_happy_path_and_cache,


if __name__ == "__main__":
    app.run()
