"""Email sender package — sends match reports via SMTP.

The sender is a no-op when the EMAIL_RECIPIENT environment variable is empty.
No recipient email address may be hard-coded here or anywhere in the codebase.
"""

from cop_thief.email_sender.email_sender import EmailSender

__all__ = ["EmailSender"]
