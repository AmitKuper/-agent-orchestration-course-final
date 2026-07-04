"""Bidirectional serialization of ``GameState`` to/from a JSON-compatible dict.

Used to persist the live game state in the ``sub_games.current_state_json``
column and reconstruct it on subsequent HTTP requests.
"""

from cop_thief.game_engine.state import GameState


def state_to_dict(state: GameState) -> dict:
    """Return a JSON-serialisable representation of *state*.

    All tuple fields are converted to lists; the barriers set is sorted.
    """
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
        "barriers": sorted([list(b) for b in state.barriers]),
        "barriers_placed": state.barriers_placed,
        "turn_counter": state.turn_counter,
        "thief_actions_completed": state.thief_actions_completed,
        "round_index": state.round_index,
        "actor_turn_index_in_round": state.actor_turn_index_in_round,
        "current_actor": state.current_actor,
        "cop_trail": [[p[0], p[1], a] for p, a in state.cop_trail.items()],
        "thief_trail": [[p[0], p[1], a] for p, a in state.thief_trail.items()],
        "game_over": state.game_over,
        "winner": state.winner,
        "win_reason": state.win_reason,
    }


def state_from_dict(d: dict) -> GameState:
    """Reconstruct a ``GameState`` from a serialised dict produced by ``state_to_dict``."""
    barriers: set = {tuple(b) for b in d["barriers"]}  # type: ignore[arg-type]
    cop_trail = {(row[0], row[1]): row[2] for row in d["cop_trail"]}
    thief_trail = {(row[0], row[1]): row[2] for row in d["thief_trail"]}
    return GameState(
        match_id=d["match_id"],
        valid_subgame_index=d["valid_subgame_index"],
        replay_attempt_index=d["replay_attempt_index"],
        grid_cols=d["grid_cols"],
        grid_rows=d["grid_rows"],
        cop_player_id=d["cop_player_id"],
        thief_player_id=d["thief_player_id"],
        cop_position=tuple(d["cop_position"]),  # type: ignore[arg-type]
        thief_position=tuple(d["thief_position"]),  # type: ignore[arg-type]
        barriers=barriers,
        barriers_placed=d["barriers_placed"],
        turn_counter=d["turn_counter"],
        thief_actions_completed=d["thief_actions_completed"],
        round_index=d["round_index"],
        actor_turn_index_in_round=d["actor_turn_index_in_round"],
        current_actor=d["current_actor"],
        cop_trail=cop_trail,
        thief_trail=thief_trail,
        game_over=d["game_over"],
        winner=d.get("winner"),
        win_reason=d.get("win_reason"),
    )
