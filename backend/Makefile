.PHONY: help install dev migrate seed setup clean test lint format check docker-build docker-up docker-down env-setup env-check

# Default target
help:
	@echo "Available commands:"
	@echo "  env-setup   - Setup environment variables (.env file)"
	@echo "  env-check   - Check if environment variables are set"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with sample data"
	@echo "  setup       - Setup database (migrate + seed)"
	@echo "  clean       - Clean cache and temporary files"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  check       - Run all checks (lint + test)"
	@echo "  docker-build - Build Docker containers"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"

# Environment setup commands
env-setup:
	python scripts/setup_env.py --setup

env-check:
	python scripts/setup_env.py --check

env-guide:
	python scripts/setup_env.py --guide

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run database migrations
migrate:
	alembic upgrade head

# Seed database with sample data
seed:
	python scripts/seed_data.py

# Setup database (migrate + seed)
setup:
	python scripts/setup_database.py

# Setup database with force seed
setup-force:
	python scripts/setup_database.py --force-seed

# Clean cache and temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 app/ tests/
	mypy app/

# Format code
format:
	black app/ tests/ scripts/
	isort app/ tests/ scripts/

# Run all checks
check: lint test

# Check database connection
check-db:
	python scripts/setup_database.py --check-only

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database backup and restore (for production)
backup-db:
	@echo "Creating database backup..."
	@echo "Note: Configure your backup command based on your database setup"

restore-db:
	@echo "Restoring database from backup..."
	@echo "Note: Configure your restore command based on your database setup"

# Generate new migration
migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Reset database (drop all tables and recreate)
reset-db:
	@echo "This will drop all database tables. Are you sure? (y/N)"
	@read confirmation; \
	if [ "$$confirmation" = "y" ] || [ "$$confirmation" = "Y" ]; then \
		alembic downgrade base; \
		alembic upgrade head; \
		python scripts/seed_data.py; \
		echo "Database reset complete"; \
	else \
		echo "Reset cancelled"; \
	fi

# Start all services for development
start-dev: docker-up
	@echo "Waiting for services to start..."
	@sleep 5
	@make setup
	@echo "Development environment ready!"
	@echo "API available at: http://localhost:8000"
	@echo "API docs at: http://localhost:8000/docs"
	@echo "Neo4j browser at: http://localhost:7474"

# Stop all services
stop-dev: docker-down
	@echo "Development environment stopped"

# Show service status
status:
	docker-compose ps

# View logs for specific service
logs-api:
	docker-compose logs -f api

logs-db:
	docker-compose logs -f postgres

logs-neo4j:
	docker-compose logs -f neo4j

logs-redis:
	docker-compose logs -f redis