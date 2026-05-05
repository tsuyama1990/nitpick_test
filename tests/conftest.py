import sys
from pathlib import Path

# Explicitly prepend the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
