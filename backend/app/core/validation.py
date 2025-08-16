from typing import List, Dict, Any
from app.models.schemas import (
    UserCreate, ProductCreate, PurchaseCreate, 
    UserInterestCreate, UserDataIngestion
)


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_user_data(user_data: Dict[str, Any]) -> UserCreate:
    """Validate and create User object from raw data"""
    try:
        return UserCreate(**user_data)
    except Exception as e:
        raise ValidationError(f"Invalid user data: {str(e)}")


def validate_product_data(product_data: Dict[str, Any]) -> ProductCreate:
    """Validate and create Product object from raw data"""
    try:
        return ProductCreate(**product_data)
    except Exception as e:
        raise ValidationError(f"Invalid product data: {str(e)}")


def validate_purchase_data(purchase_data: Dict[str, Any]) -> PurchaseCreate:
    """Validate and create Purchase object from raw data"""
    try:
        return PurchaseCreate(**purchase_data)
    except Exception as e:
        raise ValidationError(f"Invalid purchase data: {str(e)}")


def validate_interest_data(interest_data: Dict[str, Any]) -> UserInterestCreate:
    """Validate and create UserInterest object from raw data"""
    try:
        return UserInterestCreate(**interest_data)
    except Exception as e:
        raise ValidationError(f"Invalid interest data: {str(e)}")


def validate_bulk_user_data(data: Dict[str, Any]) -> UserDataIngestion:
    """Validate bulk user data ingestion"""
    try:
        return UserDataIngestion(**data)
    except Exception as e:
        raise ValidationError(f"Invalid bulk user data: {str(e)}")


def sanitize_email(email: str) -> str:
    """Sanitize email address"""
    return email.lower().strip()


def validate_confidence_score(score: float) -> float:
    """Validate and normalize confidence score"""
    if not isinstance(score, (int, float)):
        raise ValidationError("Confidence score must be a number")
    
    score = float(score)
    if not 0.0 <= score <= 1.0:
        raise ValidationError("Confidence score must be between 0.0 and 1.0")
    
    return round(score, 3)


def validate_price(price: float) -> float:
    """Validate and normalize price"""
    if not isinstance(price, (int, float)):
        raise ValidationError("Price must be a number")
    
    price = float(price)
    if price <= 0:
        raise ValidationError("Price must be greater than 0")
    
    return round(price, 2)