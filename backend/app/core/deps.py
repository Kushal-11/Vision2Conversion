"""
FastAPI dependencies for authentication and authorization
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import decode_token
from app.models.database import UserModel
from app.models.schemas import UserResponse

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserModel:
    """
    Get the current authenticated user from JWT token
    
    Args:
        db: Database session
        credentials: HTTP Authorization credentials
        
    Returns:
        Current user model
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the JWT token
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    # Extract user email/ID from token
    user_email: str = payload.get("sub")
    if user_email is None:
        raise credentials_exception
    
    # Find user in database
    user = db.query(UserModel).filter(UserModel.email == user_email).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Get current active user (wrapper for clarity)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user model
    """
    return current_user


def get_current_superuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Get current superuser (admin access required)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Superuser model
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserModel]:
    """
    Get current user if authenticated, None otherwise (for optional auth)
    
    Args:
        db: Database session
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User model if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    try:
        return get_current_user(db, credentials)
    except HTTPException:
        return None