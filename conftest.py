"""Root conftest.py - ensures src/ is on sys.path for pytest."""

import sys
from pathlib import Path
from typing import Any


def pytest_configure(config: Any) -> None:
    """Add src directory to sys.path before test collection."""
    src = str(Path(__file__).resolve().parent / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
