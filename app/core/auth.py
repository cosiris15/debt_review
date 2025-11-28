"""
Clerk Authentication Middleware

Provides JWT verification for protected API endpoints.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

from app.core.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)

# Clerk JWKS URL for token verification
CLERK_JWKS_URL = "https://direct-escargot-55.clerk.accounts.dev/.well-known/jwks.json"

# Cache for JWKS client
_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client for Clerk."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(CLERK_JWKS_URL)
    return _jwks_client


class AuthenticatedUser:
    """Represents an authenticated user from Clerk JWT."""

    def __init__(self, user_id: str, session_id: str, claims: dict):
        self.user_id = user_id
        self.session_id = session_id
        self.claims = claims

    @property
    def email(self) -> Optional[str]:
        """Get user email if available."""
        return self.claims.get("email")


async def verify_clerk_token(token: str) -> AuthenticatedUser:
    """
    Verify a Clerk JWT token and return user info.

    Args:
        token: The JWT token from Authorization header

    Returns:
        AuthenticatedUser with user info

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get signing key from Clerk JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}  # Clerk doesn't use audience
        )

        # Extract user info
        user_id = payload.get("sub")
        session_id = payload.get("sid", "")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

        return AuthenticatedUser(
            user_id=user_id,
            session_id=session_id,
            claims=payload
        )

    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthenticatedUser:
    """
    FastAPI dependency to get the current authenticated user.

    Usage:
        @app.get("/protected")
        async def protected_route(user: AuthenticatedUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await verify_clerk_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthenticatedUser]:
    """
    FastAPI dependency to optionally get the current user.
    Returns None if not authenticated (doesn't raise exception).

    Usage:
        @app.get("/public-or-private")
        async def route(user: Optional[AuthenticatedUser] = Depends(get_optional_user)):
            if user:
                return {"user_id": user.user_id}
            return {"message": "Anonymous access"}
    """
    if not credentials:
        return None

    try:
        return await verify_clerk_token(credentials.credentials)
    except HTTPException:
        return None
