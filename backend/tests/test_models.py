import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.schemas import (
    User, UserCreate, Product, ProductCreate, 
    Purchase, PurchaseCreate, UserInterest, UserInterestCreate,
    Recommendation, UserDataIngestion, InterestCategory, ProductCategory
)
from app.core.validation import (
    validate_user_data, validate_product_data, validate_purchase_data,
    validate_interest_data, validate_confidence_score, validate_price
)


class TestUserModels:
    def test_user_create_valid(self):
        user_data = {
            "email": "test@example.com",
            "profile_data": {"age": 25, "location": "NYC"}
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.profile_data["age"] == 25
    
    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email")
    
    def test_user_email_normalization(self):
        user = UserCreate(email="TEST@EXAMPLE.COM")
        assert user.email == "test@example.com"


class TestProductModels:
    def test_product_create_valid(self):
        product_data = {
            "name": "Test Product",
            "category": ProductCategory.ELECTRONICS,
            "price": 99.99,
            "description": "A test product"
        }
        product = ProductCreate(**product_data)
        assert product.name == "Test Product"
        assert product.price == 99.99
    
    def test_product_invalid_price(self):
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=-10.0
            )
    
    def test_product_price_rounding(self):
        product = ProductCreate(
            name="Test Product",
            category=ProductCategory.ELECTRONICS,
            price=99.999
        )
        assert product.price == 100.0


class TestPurchaseModels:
    def test_purchase_create_valid(self):
        purchase_data = {
            "user_id": "user123",
            "product_id": "product456",
            "amount": 99.99,
            "quantity": 2
        }
        purchase = PurchaseCreate(**purchase_data)
        assert purchase.user_id == "user123"
        assert purchase.amount == 99.99
        assert purchase.quantity == 2
    
    def test_purchase_invalid_amount(self):
        with pytest.raises(ValidationError):
            PurchaseCreate(
                user_id="user123",
                product_id="product456",
                amount=-10.0
            )


class TestUserInterestModels:
    def test_user_interest_create_valid(self):
        interest_data = {
            "user_id": "user123",
            "interest_category": InterestCategory.TECHNOLOGY,
            "interest_value": "smartphones",
            "confidence_score": 0.85,
            "source": "purchase"
        }
        interest = UserInterestCreate(**interest_data)
        assert interest.confidence_score == 0.85
        assert interest.interest_category == InterestCategory.TECHNOLOGY
    
    def test_user_interest_invalid_confidence_score(self):
        with pytest.raises(ValidationError):
            UserInterestCreate(
                user_id="user123",
                interest_category=InterestCategory.TECHNOLOGY,
                interest_value="smartphones",
                confidence_score=1.5,  # Invalid: > 1.0
                source="purchase"
            )


class TestRecommendationModels:
    def test_recommendation_valid(self):
        rec_data = {
            "product_id": "product123",
            "score": 0.92,
            "reason": "Based on purchase history",
            "category": ProductCategory.ELECTRONICS
        }
        recommendation = Recommendation(**rec_data)
        assert recommendation.score == 0.92
        assert recommendation.reason == "Based on purchase history"


class TestUserDataIngestion:
    def test_bulk_data_ingestion_valid(self):
        data = {
            "user": {
                "email": "test@example.com",
                "profile_data": {"age": 30}
            },
            "purchases": [
                {
                    "user_id": "user123",
                    "product_id": "product456",
                    "amount": 50.0
                }
            ],
            "interests": [
                {
                    "user_id": "user123",
                    "interest_category": InterestCategory.FASHION,
                    "interest_value": "sneakers",
                    "confidence_score": 0.8,
                    "source": "survey"
                }
            ]
        }
        ingestion = UserDataIngestion(**data)
        assert len(ingestion.purchases) == 1
        assert len(ingestion.interests) == 1
    
    def test_bulk_data_too_many_purchases(self):
        purchases = [
            {
                "user_id": "user123",
                "product_id": f"product{i}",
                "amount": 10.0
            } for i in range(101)  # 101 purchases (exceeds limit)
        ]
        
        with pytest.raises(ValidationError):
            UserDataIngestion(
                user={"email": "test@example.com"},
                purchases=purchases
            )


class TestValidationUtilities:
    def test_validate_confidence_score_valid(self):
        assert validate_confidence_score(0.5) == 0.5
        assert validate_confidence_score(0.999) == 0.999
        assert validate_confidence_score(0) == 0.0
        assert validate_confidence_score(1) == 1.0
    
    def test_validate_confidence_score_invalid(self):
        from app.core.validation import ValidationError
        
        with pytest.raises(ValidationError):
            validate_confidence_score(1.5)
        
        with pytest.raises(ValidationError):
            validate_confidence_score(-0.1)
        
        with pytest.raises(ValidationError):
            validate_confidence_score("invalid")
    
    def test_validate_price_valid(self):
        assert validate_price(10.99) == 10.99
        assert validate_price(100) == 100.0
        assert validate_price(0.01) == 0.01
    
    def test_validate_price_invalid(self):
        from app.core.validation import ValidationError
        
        with pytest.raises(ValidationError):
            validate_price(0)
        
        with pytest.raises(ValidationError):
            validate_price(-10.0)
        
        with pytest.raises(ValidationError):
            validate_price("invalid")
    
    def test_validate_user_data(self):
        user_data = {"email": "test@example.com"}
        user = validate_user_data(user_data)
        assert isinstance(user, UserCreate)
        assert user.email == "test@example.com"
    
    def test_validate_product_data(self):
        product_data = {
            "name": "Test Product",
            "category": "electronics",
            "price": 99.99
        }
        product = validate_product_data(product_data)
        assert isinstance(product, ProductCreate)
        assert product.name == "Test Product"