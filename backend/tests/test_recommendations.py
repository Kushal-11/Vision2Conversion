import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ProductCategory

client = TestClient(app)


class TestRecommendationsAPI:
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test user and products for recommendations"""
        # Create test user
        user_data = {
            "email": "rec_test@example.com",
            "profile_data": {"name": "Test User", "age": 30}
        }
        
        user_response = client.post("/api/v1/users/", json=user_data)
        assert user_response.status_code == 201
        self.user_id = user_response.json()["id"]
        
        # Create test products
        products = [
            {
                "name": "Test Smartphone",
                "category": ProductCategory.ELECTRONICS.value,
                "price": 699.99,
                "description": "Latest smartphone with great features"
            },
            {
                "name": "Test Laptop",
                "category": ProductCategory.ELECTRONICS.value,
                "price": 1299.99,
                "description": "High-performance laptop for professionals"
            },
            {
                "name": "Test T-Shirt",
                "category": ProductCategory.CLOTHING.value,
                "price": 24.99,
                "description": "Comfortable cotton t-shirt"
            }
        ]
        
        self.product_ids = []
        for product_data in products:
            response = client.post("/api/v1/products/", json=product_data)
            assert response.status_code == 201
            self.product_ids.append(response.json()["id"])
        
        # Add some purchase history
        purchase_data = {
            "purchases": [
                {
                    "product_id": self.product_ids[0],
                    "amount": 699.99,
                    "quantity": 1
                }
            ]
        }
        
        purchase_response = client.post(f"/api/v1/users/{self.user_id}/data", json=purchase_data)
        assert purchase_response.status_code == 201
    
    def test_get_user_recommendations(self):
        """Test getting personalized recommendations for a user"""
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Note: Recommendations might be empty if Neo4j is not available
        # but the endpoint should not fail
    
    def test_get_user_recommendations_with_limit(self):
        """Test getting recommendations with custom limit"""
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_category_recommendations(self):
        """Test getting category-specific recommendations"""
        category = ProductCategory.ELECTRONICS.value
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}/category/{category}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_similar_user_recommendations(self):
        """Test getting recommendations based on similar users"""
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}/similar")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_trending_recommendations(self):
        """Test getting trending product recommendations"""
        response = client.get("/api/v1/recommendations/trending")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_record_recommendation_interaction(self):
        """Test recording user interaction with recommendations"""
        response = client.post(
            f"/api/v1/recommendations/users/{self.user_id}/interactions"
            f"?product_id={self.product_ids[0]}&interaction_type=view"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "recorded successfully" in data["message"]
    
    def test_recommendations_user_not_found(self):
        """Test recommendations for non-existent user"""
        response = client.get("/api/v1/recommendations/users/nonexistent-user-id")
        assert response.status_code == 404
    
    def test_invalid_category_recommendations(self):
        """Test category recommendations with invalid category"""
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}/category/invalid_category")
        assert response.status_code == 422  # Validation error
    
    def test_recommendations_with_various_limits(self):
        """Test recommendations with different limit values"""
        # Test minimum limit
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        
        # Test maximum limit
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 50
        
        # Test invalid limit (should use validation)
        response = client.get(f"/api/v1/recommendations/users/{self.user_id}?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_record_different_interaction_types(self):
        """Test recording different types of interactions"""
        interaction_types = ["view", "click", "purchase"]
        
        for interaction_type in interaction_types:
            response = client.post(
                f"/api/v1/recommendations/users/{self.user_id}/interactions"
                f"?product_id={self.product_ids[0]}&interaction_type={interaction_type}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "recorded successfully" in data["message"]