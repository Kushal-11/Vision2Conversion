from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_superuser
from app.services.user_data_service import user_data_service
from app.models.database import UserModel
from app.models.schemas import UserResponse, UserUpdate, Purchase, UserDataIngestion
from app.core.validation import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# User creation is handled through /auth/register endpoint


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user by ID (users can only access their own data unless admin)"""
    # Users can only access their own data unless they're a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
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


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Get user by email (admin only)"""
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


@router.put("/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update user profile data (users can only update their own profile)"""
    # Users can only update their own profile unless they're a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's profile"
        )
    try:
        user = user_data_service.update_user_profile(db, user_id, profile_data.dict(exclude_unset=True))
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Ingest user data (purchases, interests, etc.) - users can only add to their own data"""
    # Users can only add data to their own account unless they're a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add data to this user's account"
        )
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user's purchase history (users can only access their own data)"""
    # Users can only access their own purchase history unless they're a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's purchase history"
        )
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user's spending summary (users can only access their own data)"""
    # Users can only access their own spending summary unless they're a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's spending summary"
        )
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Bulk ingest user data (user + purchases + interests) - admin only"""
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