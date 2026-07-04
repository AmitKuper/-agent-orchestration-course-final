"""Deterministic state hashing for engine synchronisation.

Both engines (local and remote) must produce identical hashes for the same
action sequence. The hash covers only canonical gameplay fields — never UI,
timestamps, messages, or actor-facing observations.
"""

import hashlib
import json

from cop_thief.game_engine.state import GameState


def _canonical_dict(state: GameState) -> dict:
    """Return a JSON-serialisable canonical representation of gameplay state."""
    return {
        "match_id": state.match_id,
        "valid_subgame_index": state.valid_subgame_index,
        "replay_attempt_index": state.replay_attempt_index,
        "grid_cols": state.grid_cols,
        "grid_rows": state.grid_rows,
        "cop_player_id": state.cop_player_id,
        "thief_player_id": state.thief_player_id,
        "cop_position": list(state.cop_position),
        "thief_position": list(state.thief_position),
        # Sort barriers so order does not affect hash
        "barriers": sorted([list(b) for b in state.barriers]),
        "barriers_placed": state.barriers_placed,
        "turn_counter": state.turn_counter,
        "thief_actions_completed": state.thief_actions_completed,
        "round_index": state.round_index,
        "actor_turn_index_in_round": state.actor_turn_index_in_round,
        "current_actor": state.current_actor,
        # Sort trail entries for determinism
        "cop_trail": sorted([[p[0], p[1], a] for p, a in state.cop_trail.items()]),
        "thief_trail": sorted([[p[0], p[1], a] for p, a in state.thief_trail.items()]),
        "game_over": state.game_over,
        "winner": state.winner,
        "win_reason": state.win_reason,
    }


def compute_state_hash(state: GameState) -> str:
    """Return a hex SHA-256 hash of the canonical true game state."""
    canonical = json.dumps(_canonical_dict(state), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def derive_subgame_seed(
    match_id: str, random_seed: int, valid_index: int, replay_attempt: int
) -> int:
    """Derive a deterministic integer seed for one sub-game.

    Formula: SHA256(match_id|random_seed|valid_index|replay_attempt)[:8 bytes].
    """
    raw = f"{match_id}|{random_seed}|{valid_index}|{replay_attempt}"
    digest = hashlib.sha256(raw.encode()).digest()
    return int.from_bytes(digest[:8], "big")
