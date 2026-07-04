"""GameEngine — the public API used by orchestrators, tests, and the SDK.

All game mechanics are delegated to focused sub-modules.
No caller outside the game_engine package should import sub-modules directly.
"""

import random

from cop_thief.game_engine.actions import Action, ActionResult
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.crumbtrails import update_crumbtrails
from cop_thief.game_engine.errors import ActionOwnershipError, EngineStateError
from cop_thief.game_engine.hashing import compute_state_hash, derive_subgame_seed
from cop_thief.game_engine.observations import build_observation
from cop_thief.game_engine.scoring import SubGameScore, score_subgame
from cop_thief.game_engine.state import COP, GameState
from cop_thief.game_engine.transitions import apply_action as _do_apply
from cop_thief.game_engine.win_conditions import check_post_action_wins

_THIEF = "thief"


def _first_actor(move_order: str, round_index: int) -> str:
    """Return the first actor for a given round based on move_order config."""
    if move_order == "thief_first":
        return _THIEF
    if move_order == "cop_first":
        return COP
    return _THIEF if round_index % 2 == 1 else COP


def _sample_positions(cols: int, rows: int, seed: int) -> tuple:
    """Sample two distinct start positions using a seeded RNG."""
    rng = random.Random(seed)
    all_cells = [(c, r) for c in range(cols) for r in range(rows)]
    rng.shuffle(all_cells)
    return tuple(all_cells[0]), tuple(all_cells[1])


class GameEngine:
    """Deterministic game rules engine for one sub-game at a time."""

    def __init__(self, config: GameConfig) -> None:
        """Bind the engine to a validated GameConfig."""
        self._cfg = config

    def initialize_subgame(
        self,
        match_id: str,
        valid_index: int,
        cop_player_id: str,
        thief_player_id: str,
        random_seed: int = 0,
        replay_attempt: int = 0,
    ) -> GameState:
        """Create a fresh GameState for a new sub-game."""
        seed = derive_subgame_seed(match_id, random_seed, valid_index, replay_attempt)
        cop_pos, thief_pos = _sample_positions(self._cfg.grid_cols, self._cfg.grid_rows, seed)
        return GameState(
            match_id=match_id,
            valid_subgame_index=valid_index,
            replay_attempt_index=replay_attempt,
            grid_cols=self._cfg.grid_cols,
            grid_rows=self._cfg.grid_rows,
            cop_player_id=cop_player_id,
            thief_player_id=thief_player_id,
            cop_position=cop_pos,
            thief_position=thief_pos,
            current_actor=_first_actor(self._cfg.move_order, 1),
        )

    def get_observation(self, state: GameState, actor: str) -> dict:
        """Return the observation dict for *actor*. Contains no hidden state."""
        return build_observation(state, actor, self._cfg)

    def apply_action(self, state: GameState, actor: str, action: Action) -> ActionResult:
        """Validate, apply, update counters, check wins, advance turn order."""
        if state.game_over:
            raise EngineStateError("Cannot apply action: sub-game is already over.")
        if actor != state.current_actor:
            raise ActionOwnershipError(f"It is {state.current_actor}'s turn, not {actor}'s.")

        result = _do_apply(state, actor, action, self._cfg)

        if result.turn_consumed:
            state.turn_counter += 1
            if actor != COP:
                state.thief_actions_completed += 1
            update_crumbtrails(state, actor, self._cfg)

            if not state.game_over:
                win = check_post_action_wins(state, actor, self._cfg)
                if win:
                    state.game_over = True
                    state.winner, state.win_reason = win

        if not state.game_over:
            self._advance_turn_order(state)

        return result

    def compute_state_hash(self, state: GameState) -> str:
        """Return the SHA-256 hash of the canonical game state."""
        return compute_state_hash(state)

    def score_subgame(self, state: GameState) -> SubGameScore:
        """Return scores for a completed sub-game."""
        return score_subgame(state, self._cfg)

    def _advance_turn_order(self, state: GameState) -> None:
        """Move to the next actor; increment round when both have acted."""
        if state.actor_turn_index_in_round == 0:
            first = _first_actor(self._cfg.move_order, state.round_index)
            state.current_actor = COP if first == _THIEF else _THIEF
            state.actor_turn_index_in_round = 1
        else:
            state.round_index += 1
            state.actor_turn_index_in_round = 0
            state.current_actor = _first_actor(self._cfg.move_order, state.round_index)
