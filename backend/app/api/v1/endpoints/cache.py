from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_cache_stats():
    """Get cache statistics and health information"""
    try:
        stats = cache_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/users/{user_id}")
async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a specific user"""
    try:
        deleted_count = cache_service.invalidate_user_cache(user_id)
        return {
            "message": f"Cache invalidated for user {user_id}",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        logger.error(f"Error invalidating cache for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/trending")
async def invalidate_trending_cache():
    """Invalidate trending products cache"""
    try:
        success = cache_service.delete("marketing_app:trending:products")
        return {
            "message": "Trending products cache invalidated",
            "success": success
        }
    except Exception as e:
        logger.error(f"Error invalidating trending cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/all")
async def flush_all_cache():
    """Flush all cache entries (use with caution)"""
    try:
        deleted_count = cache_service.delete_pattern("marketing_app:*")
        return {
            "message": "All cache entries flushed",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        logger.error(f"Error flushing all cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/health")
async def cache_health_check():
    """Check cache service health"""
    try:
        stats = cache_service.get_cache_stats()
        
        if stats.get("status") == "connected":
            return {
                "status": "healthy",
                "cache_connected": True,
                "message": "Cache service is operational"
            }
        else:
            return {
                "status": "degraded",
                "cache_connected": False,
                "message": "Cache service is not available, running without cache"
            }
    except Exception as e:
        logger.error(f"Error checking cache health: {e}")
        return {
            "status": "unhealthy",
            "cache_connected": False,
            "message": f"Cache health check failed: {str(e)}"
        }