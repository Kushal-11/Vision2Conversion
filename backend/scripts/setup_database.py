#!/usr/bin/env python3
"""
Database setup script that runs migrations and optionally seeds data
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations"""
    logger.info("Running database migrations...")
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Migrations completed successfully")
        if result.stdout:
            logger.info(f"Migration output: {result.stdout}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error("Alembic not found. Please ensure it's installed and in your PATH")
        raise


def seed_database():
    """Run database seeding"""
    logger.info("Running database seeding...")
    try:
        from scripts.seed_data import seed_database
        seed_database()
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise


def check_database_connection():
    """Check if database connection is working"""
    logger.info("Checking database connection...")
    try:
        from app.core.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met"""
    logger.info("Checking prerequisites...")
    
    # Check if .env file exists or environment variables are set
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.warning(".env file not found. Make sure environment variables are set.")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed. Please check your database configuration.")
        return False
    
    logger.info("Prerequisites check passed")
    return True


def main():
    parser = argparse.ArgumentParser(description="Database setup script")
    parser.add_argument(
        "--skip-migrations", 
        action="store_true", 
        help="Skip running migrations"
    )
    parser.add_argument(
        "--skip-seed", 
        action="store_true", 
        help="Skip seeding database with sample data"
    )
    parser.add_argument(
        "--force-seed", 
        action="store_true", 
        help="Force seed even if tables have data"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only check prerequisites and connection"
    )
    
    args = parser.parse_args()
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            logger.error("Prerequisites check failed. Exiting.")
            sys.exit(1)
        
        if args.check_only:
            logger.info("Prerequisites check completed. Database is ready.")
            return
        
        # Run migrations
        if not args.skip_migrations:
            run_migrations()
        else:
            logger.info("Skipping migrations")
        
        # Seed database
        if not args.skip_seed:
            if args.force_seed:
                logger.info("Force seeding enabled - will overwrite existing data")
            
            # Check if tables have data
            from app.core.database import SessionLocal
            from app.models.database import UserModel
            
            db = SessionLocal()
            try:
                user_count = db.query(UserModel).count()
                if user_count > 0 and not args.force_seed:
                    logger.warning(f"Database already has {user_count} users. Use --force-seed to overwrite.")
                    logger.info("Skipping seeding to preserve existing data")
                else:
                    seed_database()
            finally:
                db.close()
        else:
            logger.info("Skipping database seeding")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()