"""Pydantic schemas for match and sub-game data."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class MatchMode(StrEnum):
    """Supported game modes."""

    HUMAN_VS_SERVER = "human_vs_server"
    SERVER_VS_SERVER = "server_vs_server"
    GUEST_MCP_VS_SERVER = "guest_mcp_vs_server"


class MatchStatus(StrEnum):
    """Lifecycle status of a match."""

    LIVE = "live"
    COMPLETED = "completed"
    TECHNICAL_INVALID = "technical_invalid"
    ABORTED = "aborted"
    CANCELLED = "cancelled"


class MatchResult(StrEnum):
    """Result from the local server's perspective."""

    WON = "won"
    LOST = "lost"
    TIED = "tied"
    VOIDED = "voided"
    ABORTED = "aborted"


class MatchSummary(BaseModel):
    """Compact match representation for the history list."""

    id: int
    public_id: str
    mode: str
    status: str
    local_server_name: str
    opponent_name: str
    created_at: datetime
    result_for_local_server: str | None
    local_score: int
    opponent_score: int
    valid_subgame_count: int
    is_public: bool = True

    model_config = {"from_attributes": True}


class SubGameSummary(BaseModel):
    """Compact sub-game representation for the game detail page."""

    id: int
    index: int
    status: str
    local_role: str
    opponent_role: str
    winner_side: str | None
    win_reason: str | None
    turn_count: int

    model_config = {"from_attributes": True}


class GameEventSchema(BaseModel):
    """Public representation of a single replay event."""

    id: int
    turn_index: int
    actor_role: str
    actor_side: str
    action_json: dict
    result: str
    state_hash: str
    message_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubGameDetail(SubGameSummary):
    """Sub-game with full event log for replay."""

    started_at: datetime | None
    ended_at: datetime | None
    thief_actions: int
    barriers_used: int
    initial_state_json: dict | None
    final_state_json: dict | None
    events: list[GameEventSchema] = []


class MatchDetail(MatchSummary):
    """Full match record including sub-game list."""

    started_at: datetime | None
    ended_at: datetime | None
    rules_version: str
    config_json: dict
    is_public: bool
    sub_games: list[SubGameSummary] = []
