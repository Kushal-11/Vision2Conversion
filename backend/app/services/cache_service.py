from typing import Optional, Any, List, Dict
import redis
import json
import pickle
from app.core.config import settings
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for application data"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # We'll handle encoding/decoding manually
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _get_key(self, key_type: str, identifier: str, **kwargs) -> str:
        """Generate standardized cache keys"""
        base_key = f"marketing_app:{key_type}:{identifier}"
        if kwargs:
            suffix = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            base_key += f":{suffix}"
        return base_key
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL in seconds"""
        if not self.redis_client:
            return False
        
        try:
            # Serialize the value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = pickle.dumps(value)
            
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False
    
    # Specific cache methods for different data types
    
    def cache_user_recommendations(self, user_id: str, recommendations: List[Dict], ttl: int = 1800):
        """Cache user recommendations for 30 minutes"""
        key = self._get_key("recommendations", user_id)
        return self.set(key, recommendations, ttl)
    
    def get_user_recommendations(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user recommendations"""
        key = self._get_key("recommendations", user_id)
        return self.get(key)
    
    def cache_category_recommendations(self, user_id: str, category: str, recommendations: List[Dict], ttl: int = 3600):
        """Cache category-specific recommendations for 1 hour"""
        key = self._get_key("category_recommendations", user_id, category=category)
        return self.set(key, recommendations, ttl)
    
    def get_category_recommendations(self, user_id: str, category: str) -> Optional[List[Dict]]:
        """Get cached category recommendations"""
        key = self._get_key("category_recommendations", user_id, category=category)
        return self.get(key)
    
    def cache_trending_products(self, products: List[Dict], ttl: int = 7200):
        """Cache trending products for 2 hours"""
        key = self._get_key("trending", "products")
        return self.set(key, products, ttl)
    
    def get_trending_products(self) -> Optional[List[Dict]]:
        """Get cached trending products"""
        key = self._get_key("trending", "products")
        return self.get(key)
    
    def cache_user_interests(self, user_id: str, interests: List[Dict], ttl: int = 3600):
        """Cache user interests for 1 hour"""
        key = self._get_key("interests", user_id)
        return self.set(key, interests, ttl)
    
    def get_user_interests(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user interests"""
        key = self._get_key("interests", user_id)
        return self.get(key)
    
    def cache_user_spending_summary(self, user_id: str, summary: Dict, ttl: int = 1800):
        """Cache user spending summary for 30 minutes"""
        key = self._get_key("spending_summary", user_id)
        return self.set(key, summary, ttl)
    
    def get_user_spending_summary(self, user_id: str) -> Optional[Dict]:
        """Get cached user spending summary"""
        key = self._get_key("spending_summary", user_id)
        return self.get(key)
    
    def cache_similar_users(self, user_id: str, similar_users: List[Dict], ttl: int = 7200):
        """Cache similar users for 2 hours"""
        key = self._get_key("similar_users", user_id)
        return self.set(key, similar_users, ttl)
    
    def get_similar_users(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached similar users"""
        key = self._get_key("similar_users", user_id)
        return self.get(key)
    
    def cache_product_search(self, query: str, results: List[Dict], ttl: int = 3600):
        """Cache product search results for 1 hour"""
        # Normalize query for consistent caching
        normalized_query = query.lower().strip()
        key = self._get_key("product_search", normalized_query)
        return self.set(key, results, ttl)
    
    def get_product_search(self, query: str) -> Optional[List[Dict]]:
        """Get cached product search results"""
        normalized_query = query.lower().strip()
        key = self._get_key("product_search", normalized_query)
        return self.get(key)
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"marketing_app:recommendations:{user_id}*",
            f"marketing_app:category_recommendations:{user_id}*",
            f"marketing_app:interests:{user_id}*",
            f"marketing_app:spending_summary:{user_id}*",
            f"marketing_app:similar_users:{user_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache entries for user {user_id}")
        return total_deleted
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                ) * 100,
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}


# Create service instance
cache_service = CacheService()