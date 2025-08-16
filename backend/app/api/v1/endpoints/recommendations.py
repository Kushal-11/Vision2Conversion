from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.recommendation_service import recommendation_service
from app.services.user_data_service import user_data_service
from app.models.schemas import Recommendation, ProductCategory
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users/{user_id}", response_model=List[Recommendation])
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        recommendations = recommendation_service.get_personalized_recommendations(db, user_id, limit)
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}/category/{category}", response_model=List[Recommendation])
async def get_category_recommendations(
    user_id: str,
    category: ProductCategory,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """Get recommendations within a specific category for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        recommendations = recommendation_service.get_category_recommendations(db, user_id, category, limit)
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category recommendations for user {user_id}, category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}/similar", response_model=List[Recommendation])
async def get_similar_user_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """Get recommendations based on similar users' purchases"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        recommendations = recommendation_service.get_similar_user_recommendations(db, user_id, limit)
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar user recommendations for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/trending", response_model=List[Recommendation])
async def get_trending_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of trending recommendations to return"),
    db: Session = Depends(get_db)
):
    """Get trending product recommendations"""
    try:
        recommendations = recommendation_service.get_trending_recommendations(db, limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting trending recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/users/{user_id}/interactions")
async def record_recommendation_interaction(
    user_id: str,
    product_id: str,
    interaction_type: str = Query(..., description="Type of interaction (view, click, purchase)"),
    db: Session = Depends(get_db)
):
    """Record user interaction with recommendations"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        success = recommendation_service.record_recommendation_interaction(
            user_id, product_id, interaction_type
        )
        
        if success:
            return {"message": "Interaction recorded successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record interaction"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording interaction for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )