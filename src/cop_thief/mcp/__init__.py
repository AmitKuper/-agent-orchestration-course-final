"""MCP (Model Context Protocol) server and client package.

The server exposes game tools at /mcp for inter-group play.
The client connects to external MCP servers with SSRF protection.
"""

from cop_thief.mcp.server import router as mcp_router

__all__ = ["mcp_router"]
