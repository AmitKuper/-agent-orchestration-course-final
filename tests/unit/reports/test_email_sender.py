"""Unit tests for EmailSender — verifies no-op when recipient is empty."""

from datetime import UTC, datetime

from cop_thief.email_sender.email_sender import EmailSender
from cop_thief.reports.report_schema import MatchReport


def _report() -> MatchReport:
    """Build a minimal MatchReport fixture."""
    return MatchReport(
        match_id="m-1",
        mode="human_vs_server",
        status="completed",
        local_server_name="local",
        opponent_name="human",
        rules_version="1.0",
        local_score=20,
        opponent_score=5,
        result_for_local_server="win",
        valid_subgame_count=1,
        created_at=datetime.now(UTC),
        started_at=datetime.now(UTC),
        ended_at=datetime.now(UTC),
    )


def test_sender_not_configured_when_recipient_empty():
    """EmailSender.is_configured returns False when EMAIL_RECIPIENT is empty."""
    sender = EmailSender(settings={"recipient": "", "sender": "", "host": "", "port": 587})
    assert not sender.is_configured


def test_send_report_returns_false_when_not_configured():
    """send_report is a no-op and returns False when recipient is not set."""
    sender = EmailSender(settings={"recipient": "", "sender": "", "host": "", "port": 587})
    result = sender.send_report(_report())
    assert result is False


def test_sender_configured_when_recipient_set():
    """EmailSender.is_configured returns True when EMAIL_RECIPIENT is set."""
    settings = {"recipient": "x@example.com", "sender": "", "host": "", "port": 587}
    sender = EmailSender(settings=settings)
    assert sender.is_configured


def test_no_hardcoded_email_in_source():
    """Scan for hard-coded email addresses in the email_sender module source."""
    import inspect  # noqa: PLC0415

    from cop_thief.email_sender import email_sender as module  # noqa: PLC0415
    source = inspect.getsource(module)
    # No literal @domain.tld patterns (only the env-var string template is OK)
    import re  # noqa: PLC0415
    matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', source)
    assert matches == [], f"Hard-coded email found: {matches}"
