"""Pydantic schema for the match report format.

The report is a machine-readable JSON document summarising one completed match.
"""

from datetime import datetime

from pydantic import BaseModel


class SubGameReport(BaseModel):
    """Summary of one sub-game within the match report."""

    index: int
    local_role: str
    opponent_role: str
    winner_role: str | None
    win_reason: str | None
    turn_count: int
    thief_actions: int
    barriers_used: int
    started_at: datetime | None
    ended_at: datetime | None


class MatchReport(BaseModel):
    """Full match report — machine-readable JSON for the REST endpoint and email."""

    match_id: str
    mode: str
    status: str
    local_server_name: str
    opponent_name: str
    rules_version: str
    local_score: int
    opponent_score: int
    result_for_local_server: str | None
    valid_subgame_count: int
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    sub_games: list[SubGameReport] = []
