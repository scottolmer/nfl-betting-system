"""Dependency injection for FastAPI routes"""

from api.core.auth import get_api_key

# For Phase 1, we only have API key authentication
# Phase 2 will add:
# - get_current_user (JWT authentication)
# - get_premium_user (subscription tier checking)
# - get_db (database session)

__all__ = ["get_api_key"]
