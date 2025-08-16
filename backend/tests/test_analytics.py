import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ProductCategory

client = TestClient(app)


class TestAnalyticsAPI:
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data for analytics tests"""
        # Create test users
        users_data = [
            {
                "email": "analytics_user1@example.com",
                "profile_data": {"name": "Analytics User 1", "age": 25}
            },
            {
                "email": "analytics_user2@example.com", 
                "profile_data": {"name": "Analytics User 2", "age": 35}
            }
        ]
        
        self.user_ids = []
        for user_data in users_data:
            response = client.post("/api/v1/users/", json=user_data)
            assert response.status_code == 201
            self.user_ids.append(response.json()["id"])
        
        # Create test products
        products_data = [
            {
                "name": "Analytics Test Laptop",
                "category": ProductCategory.ELECTRONICS.value,
                "price": 999.99,
                "description": "Test laptop for analytics"
            },
            {
                "name": "Analytics Test Shirt",
                "category": ProductCategory.CLOTHING.value,
                "price": 39.99,
                "description": "Test shirt for analytics"
            }
        ]
        
        self.product_ids = []
        for product_data in products_data:
            response = client.post("/api/v1/products/", json=product_data)
            assert response.status_code == 201
            self.product_ids.append(response.json()["id"])
        
        # Create test purchases
        for i, user_id in enumerate(self.user_ids):
            purchase_data = {
                "purchases": [
                    {
                        "product_id": self.product_ids[i % len(self.product_ids)],
                        "amount": 199.99 + (i * 50),
                        "quantity": 1 + i
                    }
                ]
            }
            
            response = client.post(f"/api/v1/users/{user_id}/data", json=purchase_data)
            assert response.status_code == 201
    
    def test_get_platform_overview(self):
        """Test getting platform overview analytics"""
        response = client.get("/api/v1/analytics/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check overview structure
        assert "overview" in data
        assert "last_30_days" in data
        assert "generated_at" in data
        
        overview = data["overview"]
        assert "total_users" in overview
        assert "total_products" in overview
        assert "total_purchases" in overview
        assert "total_revenue" in overview
        assert "average_order_value" in overview
        
        last_30_days = data["last_30_days"]
        assert "new_users" in last_30_days
        assert "purchases" in last_30_days
        assert "revenue" in last_30_days
        
        # Verify data types
        assert isinstance(overview["total_users"], int)
        assert isinstance(overview["total_revenue"], (int, float))
        assert overview["total_users"] >= 2  # We created 2 users
    
    def test_get_user_analytics(self):
        """Test getting analytics for a specific user"""
        user_id = self.user_ids[0]
        response = client.get(f"/api/v1/analytics/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check user analytics structure
        assert data["user_id"] == user_id
        assert "email" in data
        assert "member_since" in data
        assert "purchase_analytics" in data
        assert "activity_summary" in data
        
        purchase_analytics = data["purchase_analytics"]
        assert "total_spent" in purchase_analytics
        assert "total_purchases" in purchase_analytics
        assert "average_purchase" in purchase_analytics
        assert "monthly_spending" in purchase_analytics
        
        # Verify data types
        assert isinstance(purchase_analytics["total_spent"], (int, float))
        assert isinstance(purchase_analytics["total_purchases"], int)
        assert purchase_analytics["total_purchases"] >= 1  # We created at least 1 purchase
    
    def test_get_product_analytics(self):
        """Test getting product analytics"""
        response = client.get("/api/v1/analytics/products")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check product analytics structure
        assert "popular_products" in data
        assert "category_performance" in data
        assert "price_distribution" in data
        assert "total_products" in data
        
        # Verify data types
        assert isinstance(data["popular_products"], list)
        assert isinstance(data["category_performance"], list)
        assert isinstance(data["price_distribution"], dict)
        assert isinstance(data["total_products"], int)
        assert data["total_products"] >= 2  # We created 2 products
    
    def test_get_product_analytics_with_limit(self):
        """Test getting product analytics with custom limit"""
        response = client.get("/api/v1/analytics/products?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["popular_products"]) <= 5
    
    def test_get_interest_analytics(self):
        """Test getting interest analytics"""
        response = client.get("/api/v1/analytics/interests")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check interest analytics structure
        assert "category_distribution" in data
        assert "source_distribution" in data
        assert "top_interests_by_category" in data
        
        # Verify data types
        assert isinstance(data["category_distribution"], list)
        assert isinstance(data["source_distribution"], list)
        assert isinstance(data["top_interests_by_category"], dict)
    
    def test_get_revenue_analytics(self):
        """Test getting revenue analytics"""
        response = client.get("/api/v1/analytics/revenue")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check revenue analytics structure
        assert "period_days" in data
        assert "start_date" in data
        assert "daily_revenue" in data
        assert "category_revenue" in data
        assert "top_customers" in data
        
        # Verify data types
        assert isinstance(data["period_days"], int)
        assert isinstance(data["daily_revenue"], list)
        assert isinstance(data["category_revenue"], list)
        assert isinstance(data["top_customers"], list)
        assert data["period_days"] == 30  # Default period
    
    def test_get_revenue_analytics_custom_period(self):
        """Test getting revenue analytics with custom period"""
        response = client.get("/api/v1/analytics/revenue?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
    
    def test_get_analytics_dashboard(self):
        """Test getting comprehensive analytics dashboard"""
        response = client.get("/api/v1/analytics/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check dashboard structure
        assert "overview" in data
        assert "top_products" in data
        assert "category_performance" in data
        assert "interest_distribution" in data
        assert "recent_revenue" in data
        assert "revenue_by_category" in data
        assert "generated_at" in data
        
        # Verify data types
        assert isinstance(data["top_products"], list)
        assert isinstance(data["category_performance"], list)
        assert isinstance(data["interest_distribution"], list)
        assert isinstance(data["recent_revenue"], list)
        assert len(data["top_products"]) <= 10  # Should be limited to top 10
    
    def test_refresh_analytics_cache(self):
        """Test refreshing analytics cache"""
        response = client.post("/api/v1/analytics/refresh")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "cleared_entries" in data
        assert "cache refreshed" in data["message"]
    
    def test_user_analytics_not_found(self):
        """Test getting analytics for non-existent user"""
        response = client.get("/api/v1/analytics/users/nonexistent-user-id")
        assert response.status_code == 404
    
    def test_revenue_analytics_invalid_period(self):
        """Test revenue analytics with invalid period"""
        # Test with period exceeding maximum
        response = client.get("/api/v1/analytics/revenue?days=400")
        assert response.status_code == 422  # Validation error
        
        # Test with negative period
        response = client.get("/api/v1/analytics/revenue?days=-5")
        assert response.status_code == 422  # Validation error
    
    def test_product_analytics_invalid_limit(self):
        """Test product analytics with invalid limit"""
        # Test with limit exceeding maximum
        response = client.get("/api/v1/analytics/products?limit=1000")
        assert response.status_code == 422  # Validation error
        
        # Test with zero limit
        response = client.get("/api/v1/analytics/products?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_analytics_caching_behavior(self):
        """Test that analytics endpoints respect caching"""
        # First request should generate fresh data
        response1 = client.get("/api/v1/analytics/overview")
        assert response1.status_code == 200
        
        # Second request should return cached data (faster)
        response2 = client.get("/api/v1/analytics/overview")
        assert response2.status_code == 200
        
        # Data should be identical
        assert response1.json() == response2.json()
        
        # After cache refresh, data should still be accessible
        refresh_response = client.post("/api/v1/analytics/refresh")
        assert refresh_response.status_code == 200
        
        response3 = client.get("/api/v1/analytics/overview")
        assert response3.status_code == 200