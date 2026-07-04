"""Application-wide constants.

All magic strings and numeric literals must be imported from here.
"""

APP_NAME = "cop-thief-server"
VERSION = "0.1.0"

# URL prefixes
API_PREFIX = "/api"
WS_PREFIX = "/ws"
MCP_PREFIX = "/mcp"

# User roles
ROLE_GUEST = "guest"
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# Match modes
MODE_HUMAN_VS_SERVER = "human_vs_server"
MODE_SERVER_VS_SERVER = "server_vs_server"
MODE_GUEST_MCP_VS_SERVER = "guest_mcp_vs_server"

# Match / sub-game statuses
STATUS_LIVE = "live"
STATUS_COMPLETED = "completed"
STATUS_TECHNICAL_INVALID = "technical_invalid"
STATUS_ABORTED = "aborted"
STATUS_CANCELLED = "cancelled"

# Local-server result values
RESULT_WON = "won"
RESULT_LOST = "lost"
RESULT_TIED = "tied"
RESULT_VOIDED = "voided"
RESULT_ABORTED = "aborted"

# Player roles
ROLE_COP = "cop"
ROLE_THIEF = "thief"

# Player sides (local vs remote opponent)
SIDE_LOCAL = "local"
SIDE_OPPONENT = "opponent"
SIDE_NONE = "none"

# Win reasons
WIN_CAPTURE = "capture"
WIN_FORFEIT = "forfeit"
WIN_TIMEOUT = "timeout"
WIN_TECHNICAL = "technical"

# Health
HEALTH_OK = "ok"

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Token algorithm
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours
