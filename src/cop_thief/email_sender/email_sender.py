"""EmailSender — sends match reports over SMTP.

The recipient address must come from the EMAIL_RECIPIENT environment variable.
This module contains NO hard-coded email addresses.
When EMAIL_RECIPIENT is empty or not set, all send calls are silently no-ops.
"""

import logging
import os
import smtplib
from email.message import EmailMessage

from cop_thief.reports.report_schema import MatchReport

logger = logging.getLogger(__name__)

_SUBJECT_TEMPLATE = "Cop & Thief match report — {match_id}"


def _load_smtp_settings() -> dict:
    """Load SMTP settings from environment variables."""
    return {
        "host": os.getenv("EMAIL_SMTP_HOST", ""),
        "port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
        "username": os.getenv("EMAIL_SMTP_USER", ""),
        "password": os.getenv("EMAIL_SMTP_PASSWORD", ""),
        "sender": os.getenv("EMAIL_SENDER", ""),
        "recipient": os.getenv("EMAIL_RECIPIENT", ""),
    }


class EmailSender:
    """Sends match report JSON over SMTP.

    All configuration comes from environment variables. When ``EMAIL_RECIPIENT``
    is empty, the sender is a no-op and logs a warning instead of raising.
    """

    def __init__(self, settings: dict | None = None) -> None:
        """Initialise from environment variables or an explicit settings dict.

        Args:
            settings: Override dict (for testing). If None, reads from env.
        """
        self._cfg = settings or _load_smtp_settings()

    @property
    def is_configured(self) -> bool:
        """Return True if a recipient address is set in the environment."""
        return bool(self._cfg.get("recipient"))

    def send_report(self, report: MatchReport) -> bool:
        """Send *report* as JSON to the configured recipient.

        Args:
            report: The completed match report to email.

        Returns:
            True if the email was sent, False if the sender is not configured.

        Raises:
            smtplib.SMTPException: On SMTP communication failure.
        """
        if not self.is_configured:
            logger.warning(
                "EMAIL_RECIPIENT not set — report for match %s not sent.",
                report.match_id,
            )
            return False

        body = report.model_dump_json(indent=2)
        msg = EmailMessage()
        msg["Subject"] = _SUBJECT_TEMPLATE.format(match_id=report.match_id)
        msg["From"] = self._cfg["sender"]
        msg["To"] = self._cfg["recipient"]
        msg.set_content(body)
        msg.add_alternative(
            f"<pre>{body}</pre>",
            subtype="html",
        )

        with smtplib.SMTP(self._cfg["host"], self._cfg["port"]) as smtp:
            smtp.starttls()
            if self._cfg["username"]:
                smtp.login(self._cfg["username"], self._cfg["password"])
            smtp.send_message(msg)

        logger.info("Report for match %s sent to configured recipient.", report.match_id)
        return True
