import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.schemas import UserCreate, PurchaseCreate

# Test database
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5433/marketing_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestUserAPI:
    def test_create_user(self):
        user_data = {
            "email": "api_test@example.com",
            "profile_data": {"age": 30, "location": "NYC"}
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "api_test@example.com"
        assert data["profile_data"]["age"] == 30
        assert "id" in data
        
        return data["id"]  # Return user ID for other tests
    
    def test_get_user_by_id(self):
        # Create a user first
        user_id = self.test_create_user()
        
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "api_test@example.com"
    
    def test_get_user_by_email(self):
        # Create a user first
        user_data = {
            "email": "email_test@example.com",
            "profile_data": {"age": 25}
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        # Get user by email
        response = client.get("/api/v1/users/email/email_test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "email_test@example.com"
    
    def test_update_user_profile(self):
        # Create a user first
        user_id = self.test_create_user()
        
        # Update profile
        profile_update = {"location": "SF", "age": 31}
        response = client.put(f"/api/v1/users/{user_id}/profile", json=profile_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["profile_data"]["location"] == "SF"
        assert data["profile_data"]["age"] == 31
    
    def test_ingest_user_data(self):
        # Create a user first
        user_id = self.test_create_user()
        
        # Ingest purchase data
        data = {
            "purchases": [
                {
                    "product_id": "laptop-123",
                    "amount": 999.99,
                    "quantity": 1
                },
                {
                    "product_id": "mouse-456",
                    "amount": 29.99,
                    "quantity": 2
                }
            ]
        }
        
        response = client.post(f"/api/v1/users/{user_id}/data", json=data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "Data ingested successfully"
        assert len(result["result"]["ingested"]) == 2
    
    def test_get_user_purchases(self):
        # Create a user and add purchases
        user_id = self.test_create_user()
        self.test_ingest_user_data()  # This adds purchases
        
        response = client.get(f"/api/v1/users/{user_id}/purchases")
        
        assert response.status_code == 200
        purchases = response.json()
        assert len(purchases) >= 2  # At least the purchases we added
    
    def test_get_spending_summary(self):
        # Create a user and add purchases
        user_id = self.test_create_user()
        self.test_ingest_user_data()  # This adds purchases
        
        response = client.get(f"/api/v1/users/{user_id}/spending-summary")
        
        assert response.status_code == 200
        summary = response.json()
        assert "total_spent" in summary
        assert "total_purchases" in summary
        assert summary["user_id"] == user_id
    
    def test_bulk_ingest(self):
        bulk_data = {
            "user": {
                "email": "bulk_test@example.com",
                "profile_data": {"age": 28}
            },
            "purchases": [
                {
                    "user_id": "placeholder",  # Will be set by service
                    "product_id": "product-1",
                    "amount": 50.0
                }
            ],
            "interests": []
        }
        
        response = client.post("/api/v1/users/bulk-ingest", json=bulk_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Bulk data ingested successfully"
    
    def test_user_not_found(self):
        response = client.get("/api/v1/users/nonexistent-id")
        assert response.status_code == 404
    
    def test_duplicate_email(self):
        user_data = {
            "email": "duplicate@example.com",
            "profile_data": {}
        }
        
        # Create first user
        response1 = client.post("/api/v1/users/", json=user_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/users/", json=user_data)
        assert response2.status_code == 400


class TestAPIHealth:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_api_root(self):
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Personalized Marketing API v1"
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"