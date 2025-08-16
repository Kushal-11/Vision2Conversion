#!/usr/bin/env python3
"""
Environment setup script to help configure environment variables
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key(length: int = 64) -> str:
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def setup_env_file():
    """Setup environment file with secure defaults"""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example_file = project_root / ".env.example"
    
    print("🔧 Setting up environment variables...")
    
    # Check if .env already exists
    if env_file.exists():
        response = input("📁 .env file already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Aborted. Keeping existing .env file.")
            return
    
    # Copy from example if it exists
    if env_example_file.exists():
        print("📋 Copying from .env.example...")
        with open(env_example_file, 'r') as f:
            content = f.read()
    else:
        print("❌ .env.example not found. Creating basic template...")
        content = create_basic_env_template()
    
    # Generate secure secret key
    secret_key = generate_secret_key()
    content = content.replace(
        "your-secret-key-change-in-production-please-use-a-strong-key",
        secret_key
    ).replace(
        "dev-secret-key-12345-change-in-production-67890-abcdef",
        secret_key
    )
    
    # Write the file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Environment file created successfully!")
    print(f"📍 Location: {env_file}")
    print("\n🔐 Generated secure secret key")
    
    # Show next steps
    print("\n📋 Next steps:")
    print("1. Review the .env file and adjust values as needed")
    print("2. Start the services: make docker-up")
    print("3. Set up the database: make setup")
    print("4. Start the development server: make dev")
    
    return env_file

def create_basic_env_template():
    """Create basic environment template if .env.example doesn't exist"""
    return """# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=marketing_db
POSTGRES_PORT=5433

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0
REDIS_PASSWORD=

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Personalized Marketing Backend

# Security
SECRET_KEY=your-secret-key-change-in-production-please-use-a-strong-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
"""

def check_env_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'POSTGRES_SERVER', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB',
        'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
        'REDIS_HOST', 'REDIS_PORT',
        'SECRET_KEY'
    ]
    
    print("🔍 Checking environment variables...")
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def show_env_guide():
    """Show guide for environment variables"""
    print("\n📖 Environment Variables Guide:")
    print("\n🗄️  Database Variables:")
    print("   POSTGRES_SERVER   - PostgreSQL server hostname (default: localhost)")
    print("   POSTGRES_USER     - Database username (default: postgres)")
    print("   POSTGRES_PASSWORD - Database password")
    print("   POSTGRES_DB       - Database name (default: marketing_db)")
    print("   POSTGRES_PORT     - Database port (default: 5433)")
    
    print("\n🕸️  Neo4j Variables:")
    print("   NEO4J_URI         - Neo4j connection URI (default: bolt://localhost:7687)")
    print("   NEO4J_USER        - Neo4j username (default: neo4j)")
    print("   NEO4J_PASSWORD    - Neo4j password")
    
    print("\n🔴 Redis Variables:")
    print("   REDIS_HOST        - Redis server hostname (default: localhost)")
    print("   REDIS_PORT        - Redis port (default: 6380)")
    print("   REDIS_DB          - Redis database number (default: 0)")
    print("   REDIS_PASSWORD    - Redis password (optional)")
    
    print("\n🔐 Security Variables:")
    print("   SECRET_KEY        - JWT secret key (auto-generated)")
    print("   ALGORITHM         - JWT algorithm (default: HS256)")
    print("   ACCESS_TOKEN_EXPIRE_MINUTES - Token expiration (default: 30)")
    
    print("\n⚙️  API Variables:")
    print("   API_V1_STR        - API version prefix (default: /api/v1)")
    print("   PROJECT_NAME      - Project name for documentation")
    print("   DEBUG             - Enable debug mode (default: true)")
    print("   LOG_LEVEL         - Logging level (default: INFO)")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Environment setup for Personalized Marketing Backend")
    parser.add_argument("--check", action="store_true", help="Check if environment variables are set")
    parser.add_argument("--guide", action="store_true", help="Show environment variables guide")
    parser.add_argument("--setup", action="store_true", help="Setup .env file")
    
    args = parser.parse_args()
    
    if args.guide:
        show_env_guide()
    elif args.check:
        # Load environment from .env file
        from dotenv import load_dotenv
        load_dotenv()
        check_env_variables()
    elif args.setup:
        setup_env_file()
    else:
        # Default: setup environment
        setup_env_file()
        
        # Also show guide
        show_env_guide()

if __name__ == "__main__":
    main()