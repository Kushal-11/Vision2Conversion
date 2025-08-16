from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics_service import analytics_service
from app.services.user_data_service import user_data_service
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_platform_overview(db: Session = Depends(get_db)):
    """Get high-level platform metrics and overview"""
    try:
        # Check cache first
        cached_overview = cache_service.get("marketing_app:analytics:overview")
        if cached_overview:
            logger.info("Returning cached platform overview")
            return cached_overview
        
        overview = analytics_service.get_platform_overview(db)
        
        # Cache for 10 minutes
        cache_service.set("marketing_app:analytics:overview", overview, ttl=600)
        
        return overview
    except Exception as e:
        logger.error(f"Error getting platform overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}")
async def get_user_analytics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check cache first
        cache_key = f"marketing_app:analytics:user:{user_id}"
        cached_analytics = cache_service.get(cache_key)
        if cached_analytics:
            logger.info(f"Returning cached user analytics for {user_id}")
            return cached_analytics
        
        user_analytics = analytics_service.get_user_analytics(db, user_id)
        
        # Cache for 30 minutes
        cache_service.set(cache_key, user_analytics, ttl=1800)
        
        return user_analytics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/products")
async def get_product_analytics(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of products to analyze"),
    db: Session = Depends(get_db)
):
    """Get product performance analytics"""
    try:
        # Check cache first
        cache_key = f"marketing_app:analytics:products:limit_{limit}"
        cached_analytics = cache_service.get(cache_key)
        if cached_analytics:
            logger.info("Returning cached product analytics")
            return cached_analytics
        
        product_analytics = analytics_service.get_product_analytics(db, limit)
        
        # Cache for 1 hour
        cache_service.set(cache_key, product_analytics, ttl=3600)
        
        return product_analytics
    except Exception as e:
        logger.error(f"Error getting product analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/interests")
async def get_interest_analytics(db: Session = Depends(get_db)):
    """Get interest and recommendation analytics"""
    try:
        # Check cache first
        cached_analytics = cache_service.get("marketing_app:analytics:interests")
        if cached_analytics:
            logger.info("Returning cached interest analytics")
            return cached_analytics
        
        interest_analytics = analytics_service.get_interest_analytics(db)
        
        # Cache for 1 hour
        cache_service.set("marketing_app:analytics:interests", interest_analytics, ttl=3600)
        
        return interest_analytics
    except Exception as e:
        logger.error(f"Error getting interest analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/revenue")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get revenue analytics for specified time period"""
    try:
        # Check cache first
        cache_key = f"marketing_app:analytics:revenue:days_{days}"
        cached_analytics = cache_service.get(cache_key)
        if cached_analytics:
            logger.info(f"Returning cached revenue analytics for {days} days")
            return cached_analytics
        
        revenue_analytics = analytics_service.get_revenue_analytics(db, days)
        
        # Cache for 30 minutes
        cache_service.set(cache_key, revenue_analytics, ttl=1800)
        
        return revenue_analytics
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/dashboard")
async def get_analytics_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive analytics dashboard data"""
    try:
        # Check cache first
        cached_dashboard = cache_service.get("marketing_app:analytics:dashboard")
        if cached_dashboard:
            logger.info("Returning cached analytics dashboard")
            return cached_dashboard
        
        # Gather all key metrics
        overview = analytics_service.get_platform_overview(db)
        product_analytics = analytics_service.get_product_analytics(db, 20)  # Top 20 products
        interest_analytics = analytics_service.get_interest_analytics(db)
        revenue_analytics = analytics_service.get_revenue_analytics(db, 30)  # Last 30 days
        
        dashboard_data = {
            "overview": overview,
            "top_products": product_analytics["popular_products"][:10],
            "category_performance": product_analytics["category_performance"],
            "interest_distribution": interest_analytics["category_distribution"],
            "recent_revenue": revenue_analytics["daily_revenue"],
            "revenue_by_category": revenue_analytics["category_revenue"],
            "generated_at": overview["generated_at"]
        }
        
        # Cache for 15 minutes
        cache_service.set("marketing_app:analytics:dashboard", dashboard_data, ttl=900)
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh")
async def refresh_analytics_cache():
    """Refresh analytics cache by clearing all cached analytics data"""
    try:
        patterns_to_clear = [
            "marketing_app:analytics:*"
        ]
        
        total_deleted = 0
        for pattern in patterns_to_clear:
            deleted = cache_service.delete_pattern(pattern)
            total_deleted += deleted
        
        return {
            "message": "Analytics cache refreshed",
            "cleared_entries": total_deleted
        }
    except Exception as e:
        logger.error(f"Error refreshing analytics cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )