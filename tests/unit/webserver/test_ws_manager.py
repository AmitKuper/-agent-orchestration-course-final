"""Unit tests for ConnectionManager — uses mock WebSockets."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cop_thief.api.ws_manager import ConnectionManager


def _mock_ws() -> MagicMock:
    """Return a mock WebSocket with async send_json and accept."""
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.fixture
def mgr() -> ConnectionManager:
    """Fresh ConnectionManager per test."""
    return ConnectionManager()


async def test_connect_accepts_websocket(mgr):
    """connect() calls ws.accept() and registers the socket."""
    ws = _mock_ws()
    await mgr.connect("match-1", ws)
    ws.accept.assert_called_once()
    assert mgr.subscriber_count("match-1") == 1


async def test_disconnect_removes_socket(mgr):
    """disconnect() deregisters the socket."""
    ws = _mock_ws()
    await mgr.connect("match-1", ws)
    await mgr.disconnect("match-1", ws)
    assert mgr.subscriber_count("match-1") == 0


async def test_disconnect_cleans_empty_key(mgr):
    """Disconnecting the last subscriber removes the match key entirely."""
    ws = _mock_ws()
    await mgr.connect("match-2", ws)
    await mgr.disconnect("match-2", ws)
    assert "match-2" not in mgr._connections


async def test_broadcast_sends_to_all_subscribers(mgr):
    """broadcast() calls send_json on every registered socket."""
    ws1, ws2 = _mock_ws(), _mock_ws()
    await mgr.connect("match-3", ws1)
    await mgr.connect("match-3", ws2)
    payload = {"event": "state_update", "observation": {}}
    await mgr.broadcast("match-3", payload)
    ws1.send_json.assert_called_once_with(payload)
    ws2.send_json.assert_called_once_with(payload)


async def test_broadcast_removes_dead_socket(mgr):
    """A socket that raises during send is silently removed."""
    ws = _mock_ws()
    ws.send_json.side_effect = RuntimeError("disconnected")
    await mgr.connect("match-4", ws)
    await mgr.broadcast("match-4", {"event": "x"})
    assert mgr.subscriber_count("match-4") == 0


async def test_broadcast_no_subscribers_is_noop(mgr):
    """Broadcasting to a match with no subscribers does not raise."""
    await mgr.broadcast("no-one", {"event": "x"})


async def test_subscriber_count_zero_for_unknown_match(mgr):
    """subscriber_count returns 0 for a match with no connections."""
    assert mgr.subscriber_count("ghost") == 0
