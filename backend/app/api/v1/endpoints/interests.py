from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_interest_service import user_interest_service
from app.services.user_data_service import user_data_service
from app.models.schemas import UserInterest, UserInterestCreate, InterestCategory
from app.core.validation import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/users/{user_id}/interests", response_model=UserInterest, status_code=status.HTTP_201_CREATED)
async def add_user_interest(
    user_id: str,
    interest_data: UserInterestCreate,
    db: Session = Depends(get_db)
):
    """Add a new interest for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ensure user_id matches
        interest_dict = interest_data.dict()
        interest_dict["user_id"] = user_id
        
        interest = user_interest_service.add_user_interest(db, interest_dict)
        return interest
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding interest for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}/interests", response_model=List[UserInterest])
async def get_user_interests(
    user_id: str,
    limit: int = Query(100, ge=1, le=500, description="Number of interests to return"),
    category: Optional[InterestCategory] = Query(None, description="Filter by interest category"),
    db: Session = Depends(get_db)
):
    """Get interests for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if category:
            interests = user_interest_service.get_interests_by_category(db, user_id, category)
        else:
            interests = user_interest_service.get_user_interests(db, user_id, limit)
        
        return interests
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interests for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users/{user_id}/interests/summary")
async def get_user_interest_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive interest summary for a user"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        summary = user_interest_service.get_interest_summary(db, user_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interest summary for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/users/{user_id}/interests/analyze")
async def analyze_user_purchase_interests(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Analyze user's purchase history to infer interests"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        generated_interests = user_interest_service.analyze_purchase_interests(db, user_id)
        
        return {
            "message": "Purchase analysis completed",
            "generated_interests_count": len(generated_interests),
            "interests": [
                {
                    "category": interest.interest_category.value,
                    "value": interest.interest_value,
                    "confidence": interest.confidence_score,
                    "source": interest.source
                }
                for interest in generated_interests
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing purchase interests for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/interests/{interest_id}")
async def update_interest_confidence(
    interest_id: str,
    new_confidence: float = Query(..., ge=0.0, le=1.0, description="New confidence score (0-1)"),
    db: Session = Depends(get_db)
):
    """Update confidence score for an interest"""
    try:
        interest = user_interest_service.update_interest_confidence(db, interest_id, new_confidence)
        if not interest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interest not found"
            )
        
        return {
            "message": "Interest confidence updated successfully",
            "interest": {
                "id": interest.id,
                "category": interest.interest_category.value,
                "value": interest.interest_value,
                "confidence": interest.confidence_score
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interest confidence for {interest_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/interests/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_interest(
    interest_id: str,
    db: Session = Depends(get_db)
):
    """Delete a user interest"""
    try:
        success = user_interest_service.delete_user_interest(db, interest_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interest not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interest {interest_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/interest-categories")
async def get_interest_categories():
    """Get all available interest categories"""
    return {
        "categories": [category.value for category in InterestCategory]
    }