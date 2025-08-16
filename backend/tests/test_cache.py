import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCacheAPI:
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test user for cache tests"""
        # Create test user
        user_data = {
            "email": "cache_test@example.com",
            "profile_data": {"name": "Cache Test User"}
        }
        
        user_response = client.post("/api/v1/users/", json=user_data)
        assert user_response.status_code == 201
        self.user_id = user_response.json()["id"]
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        response = client.get("/api/v1/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Cache stats should contain status information
        assert "status" in data
        
        # If Redis is available, we should get detailed stats
        if data["status"] == "connected":
            assert "used_memory" in data
            assert "total_keys" in data
            assert "hits" in data
            assert "misses" in data
            assert "hit_rate" in data
            assert "connected_clients" in data
        elif data["status"] == "disconnected":
            # Redis not available, but endpoint should still work
            pass
        else:
            # Error status
            assert "error" in data
    
    def test_cache_health_check(self):
        """Test cache health check endpoint"""
        response = client.get("/api/v1/cache/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Health check should always return status information
        assert "status" in data
        assert "cache_connected" in data
        assert "message" in data
        
        # Status should be one of: healthy, degraded, unhealthy
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(data["cache_connected"], bool)
    
    def test_invalidate_user_cache(self):
        """Test invalidating cache for a specific user"""
        # First, generate some cached data by making requests
        client.get(f"/api/v1/recommendations/users/{self.user_id}")
        client.get(f"/api/v1/analytics/users/{self.user_id}")
        
        # Now invalidate user cache
        response = client.delete(f"/api/v1/cache/users/{self.user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_entries" in data
        assert self.user_id in data["message"]
        assert isinstance(data["deleted_entries"], int)
    
    def test_invalidate_trending_cache(self):
        """Test invalidating trending products cache"""
        # First, generate trending cache by making request
        client.get("/api/v1/recommendations/trending")
        
        # Now invalidate trending cache
        response = client.delete("/api/v1/cache/trending")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "success" in data
        assert "trending products cache invalidated" in data["message"]
        assert isinstance(data["success"], bool)
    
    def test_flush_all_cache(self):
        """Test flushing all cache entries"""
        # First, generate some cached data
        client.get("/api/v1/analytics/overview")
        client.get(f"/api/v1/recommendations/users/{self.user_id}")
        client.get("/api/v1/recommendations/trending")
        
        # Now flush all cache
        response = client.delete("/api/v1/cache/all")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_entries" in data
        assert "All cache entries flushed" in data["message"]
        assert isinstance(data["deleted_entries"], int)
    
    def test_cache_invalidation_for_nonexistent_user(self):
        """Test cache invalidation for non-existent user"""
        response = client.delete("/api/v1/cache/users/nonexistent-user-id")
        
        # Should still succeed (returns 0 deleted entries)
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_entries"] == 0
    
    def test_cache_behavior_with_recommendations(self):
        """Test that cache works properly with recommendations endpoint"""
        # First request should populate cache
        response1 = client.get(f"/api/v1/recommendations/users/{self.user_id}")
        assert response1.status_code == 200
        
        # Second request should potentially use cache (if Redis is available)
        response2 = client.get(f"/api/v1/recommendations/users/{self.user_id}")
        assert response2.status_code == 200
        
        # Responses should be consistent
        assert response1.json() == response2.json()
        
        # Invalidate cache
        cache_response = client.delete(f"/api/v1/cache/users/{self.user_id}")
        assert cache_response.status_code == 200
        
        # Request after cache invalidation should still work
        response3 = client.get(f"/api/v1/recommendations/users/{self.user_id}")
        assert response3.status_code == 200
    
    def test_cache_behavior_with_analytics(self):
        """Test that cache works properly with analytics endpoint"""
        # First request should populate cache
        response1 = client.get("/api/v1/analytics/overview")
        assert response1.status_code == 200
        
        # Second request should potentially use cache
        response2 = client.get("/api/v1/analytics/overview")
        assert response2.status_code == 200
        
        # Responses should be consistent
        assert response1.json() == response2.json()
        
        # Refresh analytics cache
        refresh_response = client.post("/api/v1/analytics/refresh")
        assert refresh_response.status_code == 200
        
        # Request after cache refresh should still work
        response3 = client.get("/api/v1/analytics/overview")
        assert response3.status_code == 200
    
    def test_multiple_cache_operations(self):
        """Test multiple cache operations in sequence"""
        # Generate various cached data
        client.get("/api/v1/analytics/overview")
        client.get(f"/api/v1/recommendations/users/{self.user_id}")
        client.get("/api/v1/recommendations/trending")
        client.get(f"/api/v1/analytics/users/{self.user_id}")
        
        # Check cache stats
        stats_response = client.get("/api/v1/cache/stats")
        assert stats_response.status_code == 200
        
        # Invalidate user-specific cache
        user_cache_response = client.delete(f"/api/v1/cache/users/{self.user_id}")
        assert user_cache_response.status_code == 200
        
        # Invalidate trending cache
        trending_cache_response = client.delete("/api/v1/cache/trending")
        assert trending_cache_response.status_code == 200
        
        # Check cache stats again
        stats_response2 = client.get("/api/v1/cache/stats")
        assert stats_response2.status_code == 200
        
        # Finally flush all cache
        flush_response = client.delete("/api/v1/cache/all")
        assert flush_response.status_code == 200
        
        # Final stats check
        stats_response3 = client.get("/api/v1/cache/stats")
        assert stats_response3.status_code == 200