"""Domain error hierarchy for the cop-thief application."""


class CopThiefError(Exception):
    """Base error for all application errors."""


class NotFoundError(CopThiefError):
    """Raised when a requested resource does not exist."""


class PermissionError(CopThiefError):
    """Raised when an operation is not permitted for the caller."""


class ValidationError(CopThiefError):
    """Raised when input data fails domain-level validation."""


class GameError(CopThiefError):
    """Raised for illegal or invalid game operations."""


class RateLimitError(CopThiefError):
    """Raised when a caller exceeds the allowed request rate."""


class ExternalServerError(CopThiefError):
    """Raised when communication with a remote MCP server fails."""


class SSRFBlockedError(CopThiefError):
    """Raised when an external URL is blocked by SSRF protection rules."""


class GatekeeperError(CopThiefError):
    """Raised when the LLM gatekeeper rejects or fails a request."""
