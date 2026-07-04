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


class MatchDetail(MatchSummary):
    """Full match record including sub-game list."""

    started_at: datetime | None
    ended_at: datetime | None
    rules_version: str
    config_json: dict
    sub_games: list[SubGameSummary] = []
