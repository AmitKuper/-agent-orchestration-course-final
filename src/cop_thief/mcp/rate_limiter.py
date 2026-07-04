"""Per-IP rate limiter for guest MCP access.

Limits are read from ``config/rate_limits.json`` via the Gatekeeper config.
Uses a simple in-process sliding-window counter. For multi-worker deployments
this should be backed by Redis; for now it is sufficient for single-process use.
"""

import json
import time
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "rate_limits.json"


def _load_guest_limits() -> dict:
    """Load guest MCP limits from config/rate_limits.json."""
    with _CONFIG_PATH.open() as fh:
        return json.load(fh).get("guest_mcp", {})


_limits = _load_guest_limits()
_GAMES_PER_HOUR = _limits.get("games_per_hour_per_ip", 10)
_MAX_CONCURRENT = _limits.get("max_concurrent_games_per_ip", 2)

# ip → list of epoch-seconds when a game was started
_game_history: dict[str, list[float]] = {}
# ip → count of active games
_active_counts: dict[str, int] = {}


def check_and_record_new_game(client_ip: str) -> str | None:
    """Attempt to record a new game for *client_ip*.

    Returns None on success, or a rejection reason string on failure.
    """
    now = time.time()
    hour_ago = now - 3600
    history = _game_history.get(client_ip, [])
    history = [t for t in history if t > hour_ago]
    _game_history[client_ip] = history

    if len(history) >= _GAMES_PER_HOUR:
        return f"Rate limit exceeded: max {_GAMES_PER_HOUR} games per hour per IP."
    active = _active_counts.get(client_ip, 0)
    if active >= _MAX_CONCURRENT:
        return f"Too many concurrent games: max {_MAX_CONCURRENT} per IP."

    history.append(now)
    _game_history[client_ip] = history
    _active_counts[client_ip] = active + 1
    return None


def release_game(client_ip: str) -> None:
    """Decrement the active game counter for *client_ip* when a game ends."""
    count = _active_counts.get(client_ip, 0)
    if count > 0:
        _active_counts[client_ip] = count - 1
