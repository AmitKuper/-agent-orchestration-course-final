"""Unit tests for the MCP opponent allowlist."""

import json
from unittest.mock import mock_open, patch

from cop_thief.mcp.allowlist import is_origin_allowed

_OPEN = "cop_thief.mcp.allowlist.open"


def _cfg(mode: str, origins: list[str]) -> str:
    """Build a JSON allowlist config string."""
    return json.dumps({"mode": mode, "allowed_origins": origins})


def test_open_mode_allows_any_origin():
    """In open mode every origin is accepted."""
    with patch(_OPEN, mock_open(read_data=_cfg("open", []))):
        assert is_origin_allowed("any.server.com") is True


def test_restricted_mode_blocks_unknown_origin():
    """In restricted mode an unlisted origin is rejected."""
    with patch(_OPEN, mock_open(read_data=_cfg("restricted", ["good.server.com"]))):
        assert is_origin_allowed("bad.server.com") is False


def test_restricted_mode_allows_listed_origin():
    """In restricted mode a listed origin is accepted."""
    with patch(_OPEN, mock_open(read_data=_cfg("restricted", ["good.server.com"]))):
        assert is_origin_allowed("good.server.com") is True


def test_missing_mode_defaults_to_open():
    """A config without a mode key defaults to open."""
    with patch(_OPEN, mock_open(read_data=json.dumps({"allowed_origins": []}))):
        assert is_origin_allowed("anyone.example.com") is True


def test_empty_allowed_origins_in_restricted_mode_blocks_all():
    """Restricted mode with an empty list blocks every origin."""
    with patch(_OPEN, mock_open(read_data=_cfg("restricted", []))):
        assert is_origin_allowed("server.example.com") is False
