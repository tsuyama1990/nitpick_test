import os
import sys
from pathlib import Path

# Add the project root to sys.path so modules can be imported correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure dummy github token is present for testing
os.environ["GITHUB_TOKEN"] = "dummy_token_for_tests"  # noqa: S105
