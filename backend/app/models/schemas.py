from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class InterestCategory(str, Enum):
    FASHION = "fashion"
    TECHNOLOGY = "technology"
    FOOD = "food"
    TRAVEL = "travel"
    FITNESS = "fitness"
    HOME = "home"
    BEAUTY = "beauty"
    BOOKS = "books"
    MUSIC = "music"
    SPORTS = "sports"


class ProductCategory(str, Enum):
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    FOOD_BEVERAGE = "food_beverage"
    TRAVEL_SERVICES = "travel_services"
    FITNESS_EQUIPMENT = "fitness_equipment"
    HOME_GARDEN = "home_garden"
    BEAUTY_PERSONAL_CARE = "beauty_personal_care"
    BOOKS_MEDIA = "books_media"
    SPORTS_OUTDOORS = "sports_outdoors"


class UserBase(BaseModel):
    email: str = Field(..., description="User email address")
    profile_data: Dict[str, Any] = Field(default_factory=dict, description="Additional user profile information")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    category: ProductCategory = Field(..., description="Product category")
    price: float = Field(..., gt=0, description="Product price")
    description: str = Field("", max_length=1000, description="Product description")
    image_url: Optional[str] = Field(None, description="Product image URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional product metadata")
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: str = Field(..., description="Unique product identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    user_id: str = Field(..., description="User who made the purchase")
    product_id: str = Field(..., description="Product that was purchased")
    amount: float = Field(..., gt=0, description="Purchase amount")
    quantity: int = Field(1, gt=0, description="Quantity purchased")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional purchase metadata")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)


class PurchaseCreate(PurchaseBase):
    pass


class Purchase(PurchaseBase):
    id: str = Field(..., description="Unique purchase identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class UserInterestBase(BaseModel):
    user_id: str = Field(..., description="User identifier")
    interest_category: InterestCategory = Field(..., description="Category of interest")
    interest_value: str = Field(..., min_length=1, max_length=100, description="Specific interest value")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    source: str = Field(..., description="Source of interest data (e.g., 'purchase', 'survey', 'behavior')")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence score must be between 0.0 and 1.0')
        return round(v, 3)


class UserInterestCreate(UserInterestBase):
    pass


class UserInterest(UserInterestBase):
    id: str = Field(..., description="Unique interest identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class RecommendationBase(BaseModel):
    product_id: str = Field(..., description="Recommended product ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score (0-1)")
    reason: str = Field(..., description="Reason for recommendation")
    category: ProductCategory = Field(..., description="Product category")
    
    @validator('score')
    def validate_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return round(v, 3)


class Recommendation(RecommendationBase):
    pass


class UserDataIngestion(BaseModel):
    """Schema for bulk user data ingestion"""
    user: UserCreate
    purchases: List[PurchaseCreate] = Field(default_factory=list)
    interests: List[UserInterestCreate] = Field(default_factory=list)
    
    @validator('purchases')
    def validate_purchases(cls, v):
        if len(v) > 100:  # Limit batch size
            raise ValueError('Maximum 100 purchases per batch')
        return v
    
    @validator('interests')
    def validate_interests(cls, v):
        if len(v) > 50:  # Limit batch size
            raise ValueError('Maximum 50 interests per batch')
        return v


class EmailTemplateType(str, Enum):
    PERSONALIZED_RECOMMENDATIONS = "personalized_recommendations"
    WELCOME = "welcome"
    ABANDONED_CART = "abandoned_cart"
    SEASONAL_PROMOTION = "seasonal_promotion"
    INTEREST_BASED = "interest_based"
    PURCHASE_FOLLOWUP = "purchase_followup"


class EmailTemplate(BaseModel):
    """Email template schema"""
    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    template_type: EmailTemplateType = Field(..., description="Type of email template")
    subject_template: str = Field(..., description="Email subject template with placeholders")
    html_template: str = Field(..., description="HTML email body template")
    text_template: str = Field(..., description="Plain text email body template")
    variables: List[str] = Field(default_factory=list, description="Required template variables")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizedEmailRequest(BaseModel):
    """Request for generating personalized email"""
    user_id: str = Field(..., description="Target user ID")
    template_type: EmailTemplateType = Field(..., description="Type of email to generate")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional data for personalization")
    recommendations_limit: int = Field(5, ge=1, le=20, description="Number of product recommendations to include")


class GeneratedEmail(BaseModel):
    """Generated personalized email content"""
    user_id: str = Field(..., description="Target user ID")
    template_type: EmailTemplateType = Field(..., description="Email template type used")
    subject: str = Field(..., description="Personalized email subject")
    html_content: str = Field(..., description="Personalized HTML email content")
    text_content: str = Field(..., description="Personalized text email content")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Product recommendations included")
    personalization_data: Dict[str, Any] = Field(default_factory=dict, description="Data used for personalization")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class VisionBoardRequest(BaseModel):
    """Request for generating vision board"""
    user_id: str = Field(..., description="Target user ID")
    theme: Optional[str] = Field(None, description="Vision board theme")
    categories: List[ProductCategory] = Field(default_factory=list, description="Product categories to include")
    product_limit: int = Field(9, ge=4, le=16, description="Number of products to include")
    style: str = Field("modern", description="Visual style of the vision board")


class VisionBoard(BaseModel):
    """Generated vision board"""
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., description="Vision board title")
    description: str = Field(..., description="Vision board description")
    products: List[Product] = Field(..., description="Products included in vision board")
    layout_data: Dict[str, Any] = Field(..., description="Layout configuration data")
    style_config: Dict[str, Any] = Field(..., description="Style configuration")
    generated_at: datetime = Field(default_factory=datetime.utcnow)