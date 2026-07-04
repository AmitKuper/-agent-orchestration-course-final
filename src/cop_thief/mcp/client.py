"""Remote MCP client — connects to an external MCP server with SSRF protection.

Used by the orchestrator when running server-vs-server matches where the
opponent is a remote MCP-compatible game server.
"""

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from cop_thief.mcp.schemas import McpRequest, McpResponse
from cop_thief.shared.errors import SSRFBlockedError, ValidationError

# Private IPv4/IPv6 ranges that must never be contacted.
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

_TIMEOUT_SECONDS = 10


def _validate_url(url: str) -> None:
    """Raise SSRFBlockedError if *url* targets a private or disallowed address.

    Performs both syntactic checks and a DNS resolution check.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(f"MCP URL scheme must be http/https, got {parsed.scheme!r}.")
    hostname = parsed.hostname
    if not hostname:
        raise ValidationError("MCP URL must have a hostname.")
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValidationError(f"DNS resolution failed for {hostname!r}: {exc}") from exc
    for _, _, _, _, sockaddr in addr_info:
        ip = ipaddress.ip_address(sockaddr[0])
        for net in _PRIVATE_NETS:
            if ip in net:
                raise SSRFBlockedError(
                    f"MCP URL resolves to a private/restricted IP address: {ip}."
                )


class RemoteMcpClient:
    """Minimal MCP client for calling tools on a remote MCP server.

    Validates the target URL against SSRF rules before the first request
    and re-validates after each DNS resolution (defence in depth).
    """

    def __init__(self, base_url: str) -> None:
        """Bind the client to a validated remote MCP URL.

        Args:
            base_url: The URL of the remote MCP endpoint.

        Raises:
            SSRFBlockedError: If the URL resolves to a private IP.
            ValidationError: If the URL is malformed or uses a disallowed scheme.
        """
        _validate_url(base_url)
        self._base_url = base_url.rstrip("/")

    async def call_tool(self, method: str, params: dict) -> dict:
        """Call *method* on the remote MCP server with *params*.

        Args:
            method: MCP tool name (e.g. ``"list_supported_rules"``).
            params: Keyword arguments for the tool.

        Returns:
            The ``result`` dict from the MCP response.

        Raises:
            ValidationError: If the remote server returns an error.
            httpx.RequestError: On network failure.
        """
        _validate_url(self._base_url)  # re-check after potential DNS rebind
        request = McpRequest(method=method, params=params)
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as http:
            raw = await http.post(self._base_url, json=request.model_dump())
            raw.raise_for_status()
        response = McpResponse.model_validate(raw.json())
        if response.error:
            raise ValidationError(
                f"Remote MCP error {response.error.code}: {response.error.message}"
            )
        return response.result or {}
