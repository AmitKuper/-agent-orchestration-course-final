"""Unit tests for SSRF URL validation in the MCP client."""

import pytest

from cop_thief.mcp.client import _validate_url
from cop_thief.shared.errors import SSRFBlockedError, ValidationError


def test_localhost_blocked():
    """Connections to localhost must be rejected."""
    with pytest.raises(SSRFBlockedError):
        _validate_url("http://127.0.0.1/mcp")


def test_private_ip_blocked():
    """Connections to RFC-1918 private addresses must be rejected."""
    with pytest.raises(SSRFBlockedError):
        _validate_url("http://192.168.1.1/mcp")


def test_private_ip_10_blocked():
    """Connections to 10.x.x.x must be rejected."""
    with pytest.raises(SSRFBlockedError):
        _validate_url("http://10.0.0.1/mcp")


def test_link_local_blocked():
    """Connections to 169.254.x.x (cloud metadata) must be rejected."""
    with pytest.raises(SSRFBlockedError):
        _validate_url("http://169.254.169.254/mcp")


def test_invalid_scheme_rejected():
    """Non-http/https schemes must be rejected."""
    with pytest.raises(ValidationError, match="scheme"):
        _validate_url("ftp://example.com/mcp")


def test_missing_hostname_rejected():
    """URLs without a hostname must be rejected."""
    with pytest.raises(ValidationError):
        _validate_url("http:///path")


def test_dns_failure_rejected():
    """Unresolvable hostnames must be rejected."""
    with pytest.raises(ValidationError, match="DNS"):
        _validate_url("http://this-host-does-not-exist.invalid/mcp")


def test_mcp_schemas_roundtrip():
    """McpRequest and McpResponse serialise and deserialise correctly."""
    from cop_thief.mcp.schemas import McpRequest, McpResponse  # noqa: PLC0415

    req = McpRequest(method="list_supported_rules", params={}, id=1)
    d = req.model_dump()
    assert d["method"] == "list_supported_rules"

    resp = McpResponse(id=1, result={"key": "value"})
    assert resp.result["key"] == "value"
    assert resp.error is None
