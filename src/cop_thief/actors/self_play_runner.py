"""Self-play episode runner — collects trajectories for RL training.

Runs episodes where both roles use the same policy (or opponent policy),
collecting (observation, action_mask, action_index, reward) tuples.
"""

from dataclasses import dataclass, field

from cop_thief.actors.action_mask import build_action_mask
from cop_thief.actors.base import Actor
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine


@dataclass
class Trajectory:
    """One episode trajectory for RL training."""

    role: str
    observations: list[dict] = field(default_factory=list)
    action_masks: list[list[int]] = field(default_factory=list)
    action_indices: list[int] = field(default_factory=list)
    rewards: list[float] = field(default_factory=list)
    terminal_reward: float = 0.0

    def __len__(self) -> int:
        """Return the number of steps in the trajectory."""
        return len(self.observations)


class SelfPlayRunner:
    """Runs self-play episodes and collects trajectories.

    Both roles can use the same or different actors. Trajectories are
    collected from both perspectives for symmetric training.
    """

    def __init__(self, cop_actor: Actor, thief_actor: Actor, cfg: GameConfig | None = None) -> None:
        """Bind the runner to two actor instances and a game config.

        Args:
            cop_actor: Actor that plays Cop.
            thief_actor: Actor that plays Thief.
            cfg: Game config; uses ``GameConfig`` defaults if None.
        """
        self._cop = cop_actor
        self._thief = thief_actor
        self._cfg = cfg or GameConfig()
        self._engine = GameEngine(self._cfg)

    def run_episode(self, seed: int = 0) -> tuple[Trajectory, Trajectory]:
        """Run one episode and return (cop_trajectory, thief_trajectory).

        Args:
            seed: Random seed for reproducibility.

        Returns:
            Tuple of trajectories, one per role.
        """
        state = self._engine.initialize_subgame("sp", 1, "cop", "thief", random_seed=seed)
        cop_traj = Trajectory(role="cop")
        thief_traj = Trajectory(role="thief")

        while not state.game_over:
            actor = state.current_actor
            traj = cop_traj if actor == "cop" else thief_traj
            bot = self._cop if actor == "cop" else self._thief
            obs = self._engine.get_observation(state, actor)
            mask = build_action_mask(obs)
            action = bot.get_action(obs)
            # Map action back to an index (best-effort; may be -1 for unknown)
            token = action.direction or action.type
            from cop_thief.actors.action_mask import _TOKEN_INDEX  # noqa: PLC0415
            idx = _TOKEN_INDEX.get(token, 0)
            traj.observations.append(obs)
            traj.action_masks.append(mask)
            traj.action_indices.append(idx)
            traj.rewards.append(0.0)
            self._engine.apply_action(state, actor, action)

        terminal = 1.0 if state.winner == "cop" else -1.0
        cop_traj.terminal_reward = terminal
        thief_traj.terminal_reward = -terminal
        return cop_traj, thief_traj
