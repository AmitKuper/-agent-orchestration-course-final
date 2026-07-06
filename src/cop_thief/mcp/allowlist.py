"""MCP opponent allowlist — controls which remote servers may connect.

Config is read from ``config/mcp_allowlist.json``:

``mode``
    ``"open"`` — any origin may connect (default).
    ``"restricted"`` — only origins in ``allowed_origins`` may connect.

``allowed_origins``
    List of allowed hostname strings (e.g. ``"server.example.com"``).
    Compared against the ``Host`` / ``Origin`` header of each request.
    Ignored when mode is ``"open"``.
"""

from __future__ import annotations

import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "mcp_allowlist.json"


def _load() -> dict:
    """Load and return the raw allowlist config."""
    with open(_CONFIG_PATH) as fh:
        return json.load(fh)


def is_origin_allowed(origin: str) -> bool:
    """Return True if *origin* is permitted to use this MCP server.

    Args:
        origin: Hostname or IP of the calling server.

    Returns:
        True when mode is ``"open"`` or origin is in ``allowed_origins``.
    """
    cfg = _load()
    if cfg.get("mode", "open") == "open":
        return True
    return origin in cfg.get("allowed_origins", [])
