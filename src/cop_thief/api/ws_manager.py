"""WebSocket connection manager for broadcasting game observations.

Each active match has a set of connected WebSocket clients. When the
game state changes (after a human action or bot turn), the orchestrator
publishes the new observation via ``broadcast()``.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Tracks WebSocket connections grouped by match public_id.

    Thread-safety: all awaitable methods must be called from the same
    asyncio event loop as FastAPI (single-process, single-loop).
    """

    def __init__(self) -> None:
        """Initialise empty connection registry."""
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, match_id: str, ws: WebSocket) -> None:
        """Accept and register a WebSocket for *match_id*.

        Args:
            match_id: Public ID of the match to subscribe to.
            ws: Incoming WebSocket connection.
        """
        await ws.accept()
        async with self._lock:
            self._connections[match_id].add(ws)

    async def disconnect(self, match_id: str, ws: WebSocket) -> None:
        """Remove *ws* from the registry for *match_id*.

        Args:
            match_id: Public ID of the match.
            ws: WebSocket to deregister.
        """
        async with self._lock:
            self._connections[match_id].discard(ws)
            if not self._connections[match_id]:
                del self._connections[match_id]

    async def broadcast(self, match_id: str, payload: dict) -> None:
        """Send *payload* as JSON to all subscribers of *match_id*.

        Silently removes any connection that raises during send.

        Args:
            match_id: Public ID of the match.
            payload: JSON-serialisable data to push.
        """
        async with self._lock:
            sockets = set(self._connections.get(match_id, set()))
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            await self.disconnect(match_id, ws)

    def subscriber_count(self, match_id: str) -> int:
        """Return how many clients are subscribed to *match_id*."""
        return len(self._connections.get(match_id, set()))


# Process-wide singleton injected into routes.
manager = ConnectionManager()
