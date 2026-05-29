from pydantic import BaseModel


class Token(BaseModel):
    """Returned after a successful login (access + refresh pair)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Request body for the /auth/refresh endpoint."""
    refresh_token: str


class AccessToken(BaseModel):
    """Returned after a successful token refresh."""
    access_token: str
    token_type: str = "bearer"
