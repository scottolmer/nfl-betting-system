"""Minimal API key authentication for Phase 1"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from api.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Minimal auth - just API key validation.

    For development, use: X-API-Key: dev_test_key_12345
    For production, set API_KEY environment variable.

    Phase 2 will expand this to full JWT authentication with user registration/login.
    """
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key
