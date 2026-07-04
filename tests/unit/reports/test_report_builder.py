"""Unit tests for report_builder and MatchReport schema."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from cop_thief.reports.report_builder import build_report
from cop_thief.reports.report_schema import MatchReport


def _mock_match(public_id: str = "match-1") -> MagicMock:
    """Build a mock Match ORM object."""
    m = MagicMock()
    m.public_id = public_id
    m.mode = "human_vs_server"
    m.status = "completed"
    m.local_server_name = "local"
    m.opponent_name = "human"
    m.rules_version = "1.0"
    m.local_score = 20
    m.opponent_score = 5
    m.result_for_local_server = "win"
    m.valid_subgame_count = 1
    m.created_at = datetime.now(UTC)
    m.started_at = datetime.now(UTC)
    m.ended_at = datetime.now(UTC)
    m.sub_games = []
    return m


def _mock_subgame(index: int = 1) -> MagicMock:
    """Build a mock SubGame ORM object."""
    sg = MagicMock()
    sg.index = index
    sg.local_role = "cop"
    sg.opponent_role = "thief"
    sg.winner_role = "cop"
    sg.win_reason = "capture"
    sg.turn_count = 10
    sg.thief_actions = 5
    sg.barriers_used = 2
    sg.started_at = datetime.now(UTC)
    sg.ended_at = datetime.now(UTC)
    return sg


def test_build_report_returns_match_report():
    """build_report returns a MatchReport instance."""
    match = _mock_match()
    report = build_report(match)
    assert isinstance(report, MatchReport)


def test_build_report_fields_match_match_object():
    """Report fields map correctly from the Match ORM object."""
    match = _mock_match("test-123")
    report = build_report(match)
    assert report.match_id == "test-123"
    assert report.mode == "human_vs_server"
    assert report.local_score == 20


def test_build_report_with_sub_games():
    """build_report includes sub-game summaries."""
    match = _mock_match()
    sg = _mock_subgame()
    report = build_report(match, sub_games=[sg])
    assert len(report.sub_games) == 1
    assert report.sub_games[0].winner_role == "cop"


def test_build_report_validates_schema():
    """MatchReport.model_dump_json does not raise on a valid report."""
    match = _mock_match()
    report = build_report(match)
    json_str = report.model_dump_json()
    assert "match-1" in json_str


def test_report_no_hardcoded_email():
    """No email address appears anywhere in the report output."""
    match = _mock_match()
    report = build_report(match)
    json_str = report.model_dump_json()
    assert "@" not in json_str
