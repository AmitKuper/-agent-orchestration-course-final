"""GameOrchestrator — creates matches and advances the game loop.

Human-vs-server flow:
1. ``create_match`` → initialises sub-game, runs bot turns, returns observation.
2. ``apply_human_action`` → applies the human's move, runs bot turns, returns obs.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.actors.base import Actor
from cop_thief.constants import STATUS_COMPLETED, STATUS_LIVE
from cop_thief.db.models.match import Match
from cop_thief.db.models.sub_game import SubGame
from cop_thief.db.repositories import MatchRepository
from cop_thief.game.action_parser import action_from_dict
from cop_thief.game.bot_runner import run_bot_turns
from cop_thief.game.state_serializer import state_from_dict, state_to_dict
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.role_schedule import RoleSchedule
from cop_thief.shared.errors import NotFoundError, ValidationError
from cop_thief.shared.version import RULES_VERSION

_HVS_MODE = "human_vs_server"
_BOT_ID = "server_bot"
_HUMAN_ID = "human"


class GameOrchestrator:
    """Coordinates match creation and turn advancement for human-vs-server games."""

    def __init__(self, cfg: GameConfig, bot_actor: Actor) -> None:
        """Bind the orchestrator to a game config and a bot actor."""
        self._engine = GameEngine(cfg)
        self._cfg = cfg
        self._bot = bot_actor
        self._schedule = RoleSchedule.default(cfg.num_games)

    async def create_match(
        self, user_id: int, server_name: str, session: AsyncSession
    ) -> tuple[Match, dict]:
        """Create a new human-vs-server match, advance to the human's first turn.

        Returns:
            Tuple of (Match ORM object, observation dict for the human).
        """
        public_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        match = Match(
            public_id=public_id,
            mode=_HVS_MODE,
            status=STATUS_LIVE,
            local_server_name=server_name,
            opponent_name="human",
            initiator_user_id=user_id,
            created_at=now,
            started_at=now,
            rules_version=RULES_VERSION,
            config_json=self._cfg.__dict__,
        )
        session.add(match)
        await session.flush()
        sub_game, obs = await self._start_subgame(match, 1, session)  # noqa: F841
        await session.commit()
        return match, obs

    async def apply_human_action(
        self, public_id: str, action_dict: dict, session: AsyncSession
    ) -> dict:
        """Apply the human's action, advance bot turns, and return the new observation.

        Args:
            public_id: The match's public UUID.
            action_dict: Raw action dict from the API request body.
            session: Active DB session.

        Returns:
            The human player's updated observation dict.

        Raises:
            NotFoundError: If the match is not found.
            ValidationError: If the action is invalid or it is not the human's turn.
        """
        repo = MatchRepository(session)
        match = await repo.get_by_public_id(public_id)
        if match is None:
            raise NotFoundError(f"Match '{public_id}' not found.")
        sub_game = await _active_subgame(match, session)
        if sub_game is None or sub_game.current_state_json is None:
            raise ValidationError("No active sub-game state found.")
        state = state_from_dict(sub_game.current_state_json)
        human_role = sub_game.local_role
        if state.current_actor != human_role:
            raise ValidationError("It is not the human's turn.")
        action = action_from_dict(action_dict)
        self._engine.apply_action(state, human_role, action)
        run_bot_turns(self._engine, state, self._bot, human_role)
        sub_game.current_state_json = state_to_dict(state)
        if state.game_over:
            await self._close_subgame(match, sub_game, state, session)
        obs = self._engine.get_observation(state, human_role)
        await session.commit()
        return obs

    async def _start_subgame(
        self, match: Match, index: int, session: AsyncSession
    ) -> tuple[SubGame, dict]:
        """Initialise sub-game *index*, run bot turns, persist, and return the observation."""
        assignment = self._schedule.get(index)
        human_role = assignment.role_for("a")
        cop_id = _HUMAN_ID if human_role == "cop" else _BOT_ID
        thief_id = _HUMAN_ID if human_role == "thief" else _BOT_ID
        state = self._engine.initialize_subgame(match.public_id, index, cop_id, thief_id)
        run_bot_turns(self._engine, state, self._bot, human_role)
        sub_game = SubGame(
            match_id=match.id,
            index=index,
            status=STATUS_LIVE,
            local_role=human_role,
            opponent_role="cop" if human_role == "thief" else "thief",
            started_at=datetime.now(UTC),
            initial_state_json=state_to_dict(state),
            current_state_json=state_to_dict(state),
        )
        session.add(sub_game)
        await session.flush()
        obs = self._engine.get_observation(state, human_role)
        return sub_game, obs

    async def _close_subgame(
        self, match: Match, sub_game: SubGame, state, session: AsyncSession
    ) -> None:
        """Finalise the sub-game record and update match totals."""
        score = self._engine.score_subgame(state)
        sub_game.status = STATUS_COMPLETED
        sub_game.ended_at = datetime.now(UTC)
        sub_game.winner_role = state.winner
        sub_game.win_reason = state.win_reason
        sub_game.turn_count = state.turn_counter
        sub_game.thief_actions = state.thief_actions_completed
        sub_game.barriers_used = state.barriers_placed
        sub_game.final_state_json = state_to_dict(state)
        match.local_score += score.for_player(sub_game.local_role)
        match.opponent_score += score.for_player(sub_game.opponent_role)
        match.valid_subgame_count += 1


async def _active_subgame(match: Match, session: AsyncSession) -> SubGame | None:
    """Return the most recent active sub-game for *match*, or None."""
    from sqlalchemy import select  # noqa: PLC0415

    result = await session.execute(
        select(SubGame)
        .where(SubGame.match_id == match.id, SubGame.status == STATUS_LIVE)
        .order_by(SubGame.index.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
