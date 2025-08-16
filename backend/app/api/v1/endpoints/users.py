from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_data_service import user_data_service
from app.models.schemas import User, UserCreate, Purchase, UserDataIngestion
from app.core.validation import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    try:
        user = user_data_service.create_user(db, user_data.dict())
        return user
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    try:
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/email/{email}", response_model=User)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Get user by email"""
    try:
        user = user_data_service.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{user_id}/profile", response_model=User)
async def update_user_profile(
    user_id: str,
    profile_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update user profile data"""
    try:
        user = user_data_service.update_user_profile(db, user_id, profile_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{user_id}/data", status_code=status.HTTP_201_CREATED)
async def ingest_user_data(
    user_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Ingest user data (purchases, interests, etc.)"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        result = {"user_id": user_id, "ingested": []}
        
        # Process purchases if provided
        if "purchases" in data:
            for purchase_data in data["purchases"]:
                purchase = user_data_service.add_purchase(db, user_id, purchase_data)
                result["ingested"].append({
                    "type": "purchase",
                    "id": purchase.id,
                    "amount": purchase.amount
                })
        
        # TODO: Process interests when implemented
        
        return {
            "message": "Data ingested successfully",
            "result": result
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting data for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}/purchases", response_model=List[Purchase])
async def get_user_purchases(
    user_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user's purchase history"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        purchases = user_data_service.get_user_purchases(db, user_id, limit)
        return purchases
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting purchases for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}/spending-summary")
async def get_user_spending_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's spending summary"""
    try:
        # Verify user exists
        user = user_data_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        summary = user_data_service.get_user_spending_summary(db, user_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting spending summary for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/bulk-ingest")
async def bulk_ingest_user_data(
    bulk_data: UserDataIngestion,
    db: Session = Depends(get_db)
):
    """Bulk ingest user data (user + purchases + interests)"""
    try:
        result = user_data_service.ingest_bulk_user_data(db, bulk_data.dict())
        return {
            "message": "Bulk data ingested successfully",
            "result": result
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during bulk data ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )