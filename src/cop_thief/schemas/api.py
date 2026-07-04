"""General-purpose API schemas (health, auth, pagination)."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for GET /api/health."""

    status: str
    version: str
    server_name: str


class LoginRequest(BaseModel):
    """Request body for POST /api/auth/login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response body containing a JWT access token."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public representation of the authenticated user."""

    id: int
    username: str
    display_name: str
    role: str

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    """Generic wrapper for paginated list responses."""

    total: int
    offset: int
    limit: int
    items: list
