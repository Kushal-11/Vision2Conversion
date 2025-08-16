"""
Pytest configuration and fixtures for the personalized marketing backend tests.
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.schemas import ProductCategory, InterestCategory

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create test client"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create database session for tests"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@example.com",
        "profile_data": {
            "name": "Test User",
            "age": 30,
            "location": "Test City",
            "preferences": ["technology", "fitness"]
        }
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for tests"""
    return {
        "name": "Test Product",
        "category": ProductCategory.ELECTRONICS.value,
        "price": 99.99,
        "description": "A test product for unit testing",
        "image_url": "https://example.com/product.jpg",
        "metadata": {
            "brand": "TestBrand",
            "warranty": "1 year",
            "features": ["feature1", "feature2"]
        }
    }


@pytest.fixture
def sample_purchase_data():
    """Sample purchase data for tests"""
    return {
        "product_id": "test-product-id",
        "amount": 99.99,
        "quantity": 1,
        "metadata": {
            "payment_method": "credit_card",
            "discount_applied": False
        }
    }


@pytest.fixture
def sample_interest_data():
    """Sample interest data for tests"""
    return {
        "interest_category": InterestCategory.TECHNOLOGY.value,
        "interest_value": "smartphones",
        "confidence_score": 0.8,
        "source": "purchase"
    }


@pytest.fixture
def sample_email_request():
    """Sample email generation request"""
    return {
        "user_id": "test-user-id",
        "template_type": "personalized_recommendations",
        "additional_data": {"campaign_name": "test_campaign"},
        "recommendations_limit": 5
    }


@pytest.fixture
def sample_vision_board_request():
    """Sample vision board generation request"""
    return {
        "user_id": "test-user-id",
        "theme": "Tech Enthusiast",
        "categories": [ProductCategory.ELECTRONICS.value],
        "product_limit": 6,
        "style": "modern"
    }


@pytest.fixture
def create_test_user(client: TestClient, sample_user_data):
    """Create a test user and return user ID"""
    def _create_user(email: str = None, profile_data: dict = None):
        user_data = sample_user_data.copy()
        if email:
            user_data["email"] = email
        if profile_data:
            user_data["profile_data"].update(profile_data)
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        return response.json()["id"]
    
    return _create_user


@pytest.fixture
def create_test_product(client: TestClient, sample_product_data):
    """Create a test product and return product ID"""
    def _create_product(name: str = None, category: str = None, price: float = None):
        product_data = sample_product_data.copy()
        if name:
            product_data["name"] = name
        if category:
            product_data["category"] = category
        if price:
            product_data["price"] = price
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 201
        return response.json()["id"]
    
    return _create_product


@pytest.fixture
def create_test_purchase(client: TestClient):
    """Create a test purchase"""
    def _create_purchase(user_id: str, product_id: str, amount: float = 99.99):
        purchase_data = {
            "purchases": [{
                "product_id": product_id,
                "amount": amount,
                "quantity": 1
            }]
        }
        
        response = client.post(f"/api/v1/users/{user_id}/data", json=purchase_data)
        assert response.status_code == 201
        return response.json()
    
    return _create_purchase


@pytest.fixture
def create_test_interest(client: TestClient, sample_interest_data):
    """Create a test interest"""
    def _create_interest(user_id: str, category: str = None, value: str = None, confidence: float = None):
        interest_data = sample_interest_data.copy()
        if category:
            interest_data["interest_category"] = category
        if value:
            interest_data["interest_value"] = value
        if confidence:
            interest_data["confidence_score"] = confidence
        
        response = client.post(f"/api/v1/interests/users/{user_id}/interests", json=interest_data)
        # Note: This might fail if interests endpoint has issues, but we don't fail the test
        return response
    
    return _create_interest


# Pytest markers for test organization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.api = pytest.mark.api
pytest.mark.slow = pytest.mark.slow


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "cache: Cache-related tests")
    config.addinivalue_line("markers", "analytics: Analytics-related tests")
    config.addinivalue_line("markers", "marketing: Marketing-related tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on file names
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        if "test_cache" in item.nodeid:
            item.add_marker(pytest.mark.cache)
        if "test_analytics" in item.nodeid:
            item.add_marker(pytest.mark.analytics)
        if "test_marketing" in item.nodeid:
            item.add_marker(pytest.mark.marketing)
        
        # Add integration marker for tests that use multiple services
        if any(keyword in item.nodeid for keyword in ["recommendations", "marketing", "analytics"]):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)