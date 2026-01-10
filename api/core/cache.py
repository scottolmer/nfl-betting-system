"""Redis caching utilities"""

import redis.asyncio as redis
import json
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    logger.info("✓ Redis client initialized")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    redis_client = None


async def cache_get(key: str) -> Optional[str]:
    """Get value from cache"""
    if not redis_client:
        return None
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: str, expire: int = 3600):
    """Set value in cache with expiration (default 1 hour)"""
    if not redis_client:
        return
    try:
        await redis_client.setex(key, expire, value)
    except Exception as e:
        logger.warning(f"Cache set error: {e}")


async def cache_delete(key: str):
    """Delete key from cache"""
    if not redis_client:
        return
    try:
        await redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")


async def cache_invalidate_week(week: int):
    """Invalidate all cache entries for a given week"""
    if not redis_client:
        return
    try:
        pattern = f"*week_{week}*"
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries for week {week}")
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")
