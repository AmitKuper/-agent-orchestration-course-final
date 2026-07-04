"""Unit tests for version consistency across the three version sources."""

import json
import tomllib
from pathlib import Path

from cop_thief.shared.version import VERSION

REPO_ROOT = Path(__file__).parents[2]


def test_version_matches_pyproject() -> None:
    """VERSION in shared/version.py must match pyproject.toml."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["project"]["version"] == VERSION, (
        f"shared/version.py VERSION={VERSION!r} does not match pyproject.toml"
    )


def test_version_matches_rate_limits() -> None:
    """VERSION in shared/version.py must match config/rate_limits.json."""
    with open(REPO_ROOT / "config" / "rate_limits.json") as f:
        data = json.load(f)
    assert data["version"] == VERSION, (
        f"shared/version.py VERSION={VERSION!r} does not match config/rate_limits.json"
    )
