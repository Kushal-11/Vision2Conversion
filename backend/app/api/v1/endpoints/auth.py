"""
Authentication endpoints for user registration, login, and password management
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    create_password_reset_token,
    verify_password_reset_token
)
from app.core.deps import get_current_user, get_current_active_user
from app.core.config import settings
from app.models.database import UserModel
from app.models.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    PasswordResetRequest,
    PasswordReset
)
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify basic functionality"""
    return {"message": "Auth endpoint is working", "status": "ok"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
        user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            profile_data=user_data.profile_data,
            is_active=True,
            is_superuser=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Cache user data (don't fail if cache is unavailable)
        try:
            cache_service.set(f"user:{user.id}", {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }, ttl=3600)
        except Exception as e:
            # Log cache error but don't fail registration
            print(f"Failed to cache user data: {e}")
        
        # Convert to response model
        try:
            response = UserResponse.from_orm(user)
            return response
        except Exception as e:
            print(f"Error converting user to response: {e}")
            # Fallback: create response manually
            return UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                profile_data=user.profile_data,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    Login user and return access token
    
    Args:
        form_data: OAuth2 form data (username/email and password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    # Cache user session
    cache_service.set(f"session:{user.id}", {
        "user_id": user.id,
        "email": user.email,
        "login_at": user.updated_at.isoformat() if user.updated_at else None
    }, ttl=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login/json", response_model=Token)
def login_user_json(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Login user with JSON payload and return access token
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    # Cache user session
    cache_service.set(f"session:{user.id}", {
        "user_id": user.id,
        "email": user.email,
        "login_at": user.updated_at.isoformat() if user.updated_at else None
    }, ttl=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout")
def logout_user(
    current_user: UserModel = Depends(get_current_active_user)
) -> dict:
    """
    Logout current user (invalidate session cache)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # Clear user session from cache
    cache_service.delete(f"session:{current_user.id}")
    
    # Clear user data from cache
    cache_service.delete(f"user:{current_user.id}")
    
    return {"message": "Successfully logged out"}


@router.post("/password-reset-request")
def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Request password reset token
    
    Args:
        request_data: Password reset request data
        db: Database session
        
    Returns:
        Success message (always returns success for security)
    """
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == request_data.email).first()
    
    if user and user.is_active:
        # Generate password reset token
        reset_token = create_password_reset_token(user.email)
        
        # Cache the reset token temporarily (1 hour)
        cache_service.set(f"reset_token:{user.id}", {
            "token": reset_token,
            "email": user.email,
            "created_at": user.updated_at.isoformat() if user.updated_at else None
        }, ttl=3600)
        
        # In a real application, you would send this token via email
        # For demo purposes, we'll just cache it
        print(f"Password reset token for {user.email}: {reset_token}")
    
    # Always return success message for security (don't reveal if email exists)
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset")
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
) -> dict:
    """
    Reset user password using reset token
    
    Args:
        reset_data: Password reset data with token and new password
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    # Verify the reset token
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()
    
    # Clear any cached user data and reset tokens
    cache_service.delete(f"user:{user.id}")
    cache_service.delete(f"session:{user.id}")
    cache_service.delete(f"reset_token:{user.id}")
    
    return {"message": "Password successfully reset"}


@router.get("/verify-token")
def verify_token(
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    """
    Verify if the current token is valid
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Token verification status
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }