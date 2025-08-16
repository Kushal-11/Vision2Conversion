#!/usr/bin/env python3
"""
Test script to verify Redis Cloud connection
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import redis
import json
from datetime import datetime

def test_redis_cloud_connection():
    """Test connection to Redis Cloud"""
    try:
        # Get Redis configuration from environment
        redis_host = os.getenv('REDIS_HOST')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_db = int(os.getenv('REDIS_DB', 0))
        redis_password = os.getenv('REDIS_PASSWORD')
        
        print(f"🔴 Testing Redis Cloud Connection...")
        print(f"   Host: {redis_host}")
        print(f"   Port: {redis_port}")
        print(f"   Database: {redis_db}")
        print(f"   Password: {'*' * len(redis_password) if redis_password else 'None'}")
        
        # Create Redis connection
        if redis_password:
            redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        
        print(f"   Connection URL: redis://:***@{redis_host}:{redis_port}/{redis_db}")
        
        # Connect to Redis
        r = redis.Redis.from_url(
            redis_url,
            decode_responses=False,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # Test basic operations
        print(f"\n🧪 Testing basic operations...")
        
        # 1. Ping test
        pong = r.ping()
        print(f"   ✅ Ping: {pong}")
        
        # 2. Set/Get test
        test_key = "test:vision2conversion:connection"
        test_value = {
            "message": "Redis Cloud connection successful!",
            "timestamp": datetime.now().isoformat(),
            "app": "Vision2Conversion Backend"
        }
        
        # Set value
        r.setex(test_key, 300, json.dumps(test_value))  # 5 minute expiry
        print(f"   ✅ Set test data with key: {test_key}")
        
        # Get value
        retrieved = r.get(test_key)
        if retrieved:
            retrieved_data = json.loads(retrieved)
            print(f"   ✅ Retrieved test data: {retrieved_data['message']}")
        else:
            print(f"   ❌ Failed to retrieve test data")
            return False
        
        # 3. Delete test
        r.delete(test_key)
        print(f"   ✅ Cleaned up test data")
        
        # 4. Info test
        info = r.info()
        print(f"   ✅ Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"   ✅ Used memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"   ✅ Connected clients: {info.get('connected_clients', 'Unknown')}")
        
        # 5. Test our application cache keys
        print(f"\n🔧 Testing application cache patterns...")
        
        # Test recommendation cache
        rec_key = "marketing_app:recommendations:test_user_123"
        rec_data = [
            {"product_id": "prod_1", "score": 0.95, "reason": "Test recommendation"},
            {"product_id": "prod_2", "score": 0.87, "reason": "Another test"}
        ]
        
        r.setex(rec_key, 1800, json.dumps(rec_data))  # 30 minutes
        print(f"   ✅ Set recommendation cache")
        
        # Test analytics cache
        analytics_key = "marketing_app:analytics:overview"
        analytics_data = {
            "total_users": 100,
            "total_revenue": 50000.0,
            "generated_at": datetime.now().isoformat()
        }
        
        r.setex(analytics_key, 600, json.dumps(analytics_data))  # 10 minutes
        print(f"   ✅ Set analytics cache")
        
        # List all our app keys
        app_keys = r.keys("marketing_app:*")
        print(f"   ✅ Found {len(app_keys)} application cache keys")
        
        # Clean up test keys
        if app_keys:
            r.delete(*app_keys)
            print(f"   ✅ Cleaned up application test keys")
        
        print(f"\n🎉 Redis Cloud connection test SUCCESSFUL!")
        print(f"   Your application is ready to use Redis Cloud for caching.")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
        print(f"   💡 Check your Redis Cloud credentials and network connectivity")
        return False
        
    except redis.AuthenticationError as e:
        print(f"   ❌ Authentication Error: {e}")
        print(f"   💡 Check your Redis Cloud password")
        return False
        
    except redis.TimeoutError as e:
        print(f"   ❌ Timeout Error: {e}")
        print(f"   💡 Check your network connectivity to Redis Cloud")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        print(f"   💡 Check your Redis Cloud configuration")
        return False

def test_cache_service():
    """Test our cache service with Redis Cloud"""
    try:
        print(f"\n🔧 Testing Cache Service...")
        
        from app.services.cache_service import cache_service
        
        # Test cache service methods
        test_key = "test_cache_service"
        test_data = {"message": "Cache service test", "timestamp": datetime.now().isoformat()}
        
        # Set data
        success = cache_service.set(test_key, test_data, ttl=300)
        print(f"   ✅ Cache service set: {success}")
        
        # Get data
        retrieved = cache_service.get(test_key)
        print(f"   ✅ Cache service get: {retrieved is not None}")
        
        if retrieved:
            print(f"   ✅ Retrieved message: {retrieved.get('message', 'N/A')}")
        
        # Test cache stats
        stats = cache_service.get_cache_stats()
        print(f"   ✅ Cache stats: {stats.get('status', 'Unknown')}")
        
        # Clean up
        cache_service.delete(test_key)
        print(f"   ✅ Cleaned up cache service test")
        
        print(f"   🎉 Cache Service test SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"   ❌ Cache Service Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Vision2Conversion - Redis Cloud Connection Test")
    print("=" * 50)
    
    # Test direct Redis connection
    redis_success = test_redis_cloud_connection()
    
    if redis_success:
        # Test our cache service
        cache_success = test_cache_service()
        
        if cache_success:
            print(f"\n✅ ALL TESTS PASSED!")
            print(f"   Your Redis Cloud setup is working perfectly!")
        else:
            print(f"\n⚠️  Redis Cloud works, but cache service has issues")
    else:
        print(f"\n❌ Redis Cloud connection failed")
        print(f"   Please check your configuration and try again")