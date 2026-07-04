"""Report builder — assembles a MatchReport from ORM objects.

Converts Match and SubGame ORM instances into a validated MatchReport.
"""

from cop_thief.db.models.match import Match
from cop_thief.db.models.sub_game import SubGame
from cop_thief.reports.report_schema import MatchReport, SubGameReport


def build_report(match: Match, sub_games: list[SubGame] | None = None) -> MatchReport:
    """Build a ``MatchReport`` from a ``Match`` ORM object and its sub-games.

    Args:
        match: The completed (or in-progress) match ORM record.
        sub_games: Optional list of ``SubGame`` records; uses ``match.sub_games``
                   if not provided.

    Returns:
        A validated ``MatchReport`` instance ready for serialisation.
    """
    games = sub_games if sub_games is not None else (match.sub_games or [])
    sub_reports = [
        SubGameReport(
            index=sg.index,
            local_role=sg.local_role,
            opponent_role=sg.opponent_role,
            winner_role=sg.winner_role,
            win_reason=sg.win_reason,
            turn_count=sg.turn_count,
            thief_actions=sg.thief_actions,
            barriers_used=sg.barriers_used,
            started_at=sg.started_at,
            ended_at=sg.ended_at,
        )
        for sg in games
    ]
    return MatchReport(
        match_id=match.public_id,
        mode=match.mode,
        status=match.status,
        local_server_name=match.local_server_name,
        opponent_name=match.opponent_name,
        rules_version=match.rules_version,
        local_score=match.local_score,
        opponent_score=match.opponent_score,
        result_for_local_server=match.result_for_local_server,
        valid_subgame_count=match.valid_subgame_count,
        created_at=match.created_at,
        started_at=match.started_at,
        ended_at=match.ended_at,
        sub_games=sub_reports,
    )
