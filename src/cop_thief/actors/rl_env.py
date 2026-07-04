"""Gym-compatible RL environment wrapping the game engine.

Exposes a step/reset interface for reinforcement learning frameworks.
Rewards are calculated per action based on game outcomes and distance heuristics.
"""

from cop_thief.actors.action_mask import build_action_mask, vocab_size
from cop_thief.actors.random_actor import RandomLegalActor, _parse_candidate
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.state import GameState

_REWARD_WIN = 1.0
_REWARD_LOSS = -1.0
_REWARD_STEP = 0.0


class CopThiefEnv:
    """Single-agent Gym-like environment for one cop OR thief perspective.

    The agent controls one role; the opponent is played by ``RandomLegalActor``.
    Episodes correspond to one sub-game. Actions are selected from the
    fixed-size action mask vocabulary (10 slots: 8 dirs + stay + forfeit).
    """

    def __init__(self, role: str = "cop", cfg: GameConfig | None = None) -> None:
        """Initialise the environment for *role* ('cop' or 'thief').

        Args:
            role: The role the RL agent plays.
            cfg: Game config; uses default ``GameConfig`` if None.
        """
        self._role = role
        self._cfg = cfg or GameConfig()
        self._engine = GameEngine(self._cfg)
        self._opponent = RandomLegalActor()
        self._state: GameState | None = None
        self._ep = 0

    @property
    def action_space_size(self) -> int:
        """Return the number of discrete actions (vocabulary size)."""
        return vocab_size()

    def reset(self) -> dict:
        """Reset to a fresh sub-game and return the initial observation.

        Returns:
            Observation dict for the agent's role.
        """
        self._ep += 1
        cop_id = "agent" if self._role == "cop" else "opponent"
        thief_id = "agent" if self._role == "thief" else "opponent"
        self._state = self._engine.initialize_subgame(
            f"ep{self._ep}", 1, cop_id, thief_id, random_seed=self._ep
        )
        self._advance_opponent()
        return self._engine.get_observation(self._state, self._role)

    def step(self, action_index: int) -> tuple[dict, float, bool]:
        """Apply *action_index* for the agent and advance the opponent.

        Args:
            action_index: Index into the action mask vocabulary.

        Returns:
            Tuple of (observation, reward, done).
        """
        if self._state is None or self._state.game_over:
            raise RuntimeError("Call reset() before step().")
        obs = self._engine.get_observation(self._state, self._role)
        mask = build_action_mask(obs)
        if mask[action_index] == 0:
            # Illegal action — treat as stay if enabled, else stay
            token = "stay" if self._cfg.stay_enabled else "N"
        else:
            from cop_thief.actors.action_mask import action_token_at  # noqa: PLC0415
            token = action_token_at(action_index)
        action = _parse_candidate(token)
        self._engine.apply_action(self._state, self._role, action)
        if not self._state.game_over:
            self._advance_opponent()
        reward = self._compute_reward()
        obs = self._engine.get_observation(self._state, self._role)
        return obs, reward, self._state.game_over

    def _advance_opponent(self) -> None:
        """Run opponent turns until the agent's turn or game over."""
        while not self._state.game_over and self._state.current_actor != self._role:
            opp_role = self._state.current_actor
            obs = self._engine.get_observation(self._state, opp_role)
            action = self._opponent.get_action(obs)
            self._engine.apply_action(self._state, opp_role, action)

    def _compute_reward(self) -> float:
        """Return the reward signal for the current state."""
        if not self._state.game_over:
            return _REWARD_STEP
        if self._state.winner == self._role:
            return _REWARD_WIN
        return _REWARD_LOSS
