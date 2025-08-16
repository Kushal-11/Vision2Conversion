# Project Structure

This document explains the organization and architecture of the Vision2Conversion backend.

## 📁 Directory Structure

```
backend/
├── app/                          # Main application package
│   ├── api/                     # API layer
│   │   └── v1/                  # API version 1
│   │       ├── endpoints/       # API endpoint implementations
│   │       │   ├── analytics.py # Analytics and metrics endpoints
│   │       │   ├── cache.py     # Cache management endpoints
│   │       │   ├── interests.py # User interests endpoints
│   │       │   ├── marketing.py # Marketing automation endpoints
│   │       │   ├── products.py  # Product catalog endpoints
│   │       │   ├── recommendations.py # Recommendation endpoints
│   │       │   └── users.py     # User management endpoints
│   │       └── api.py           # API router configuration
│   ├── core/                    # Core application modules
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection setup
│   │   └── validation.py       # Data validation utilities
│   ├── models/                  # Data models
│   │   ├── database.py         # SQLAlchemy database models
│   │   └── schemas.py          # Pydantic schemas for validation
│   ├── repositories/            # Data access layer
│   │   ├── base.py             # Base repository class
│   │   ├── product.py          # Product data access
│   │   ├── purchase.py         # Purchase data access
│   │   ├── user.py             # User data access
│   │   └── user_interest.py    # User interest data access
│   ├── services/                # Business logic layer
│   │   ├── analytics_service.py     # Business analytics
│   │   ├── cache_service.py         # Caching operations
│   │   ├── knowledge_graph_service.py # Neo4j operations
│   │   ├── marketing_service.py     # Email generation
│   │   ├── product_service.py       # Product management
│   │   ├── recommendation_service.py # Recommendation engine
│   │   ├── user_data_service.py     # User data management
│   │   ├── user_interest_service.py # Interest tracking
│   │   └── vision_board_service.py  # Vision board generation
│   └── main.py                  # FastAPI application entry point
├── alembic/                     # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Migration template
├── scripts/                     # Utility scripts
│   ├── seed_data.py            # Database seeding
│   ├── setup_database.py       # Database setup
│   └── setup_env.py            # Environment setup
├── tests/                       # Test suite
│   ├── conftest.py             # Test configuration
│   ├── test_analytics.py       # Analytics tests
│   ├── test_api.py             # API endpoint tests
│   ├── test_cache.py           # Cache functionality tests
│   ├── test_marketing.py       # Marketing feature tests
│   ├── test_products.py        # Product management tests
│   └── test_recommendations.py # Recommendation tests
├── .env.example                # Environment template
├── docker-compose.yml          # Docker services configuration
├── requirements.txt            # Python dependencies
├── Makefile                    # Development commands
└── README.md                   # Backend documentation
```

## 🏗️ Architecture Layers

### 1. API Layer (`app/api/`)
- **Purpose**: HTTP request/response handling
- **Components**: FastAPI routers and endpoints
- **Responsibilities**:
  - Request validation
  - Response serialization
  - HTTP status code management
  - Authentication (when implemented)

### 2. Service Layer (`app/services/`)
- **Purpose**: Business logic implementation
- **Components**: Service classes for different domains
- **Responsibilities**:
  - Complex business operations
  - Cross-repository coordination
  - External service integration
  - Data transformation

### 3. Repository Layer (`app/repositories/`)
- **Purpose**: Data access abstraction
- **Components**: Repository classes for database entities
- **Responsibilities**:
  - Database query implementation
  - Data persistence
  - Query optimization
  - Database-specific logic

### 4. Model Layer (`app/models/`)
- **Purpose**: Data structure definitions
- **Components**: 
  - `database.py`: SQLAlchemy ORM models
  - `schemas.py`: Pydantic validation schemas
- **Responsibilities**:
  - Data validation
  - Serialization/deserialization
  - Type safety

### 5. Core Layer (`app/core/`)
- **Purpose**: Foundation utilities
- **Components**: Configuration, database setup, validation
- **Responsibilities**:
  - Application configuration
  - Database connection management
  - Shared utilities

## 📊 Data Flow

```
HTTP Request
    ↓
API Endpoint (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database (PostgreSQL/Neo4j/Redis)
```

## 🗄️ Database Architecture

### PostgreSQL (Primary Database)
- **Tables**: users, products, purchases, user_interests
- **Purpose**: Relational data storage
- **Access**: Via SQLAlchemy ORM

### Neo4j (Knowledge Graph)
- **Nodes**: User, Product, Interest Category, Interest Value
- **Relationships**: PURCHASED, INTERESTED_IN, BELONGS_TO
- **Purpose**: Recommendation algorithms
- **Access**: Via neo4j Python driver

### Redis (Cache Layer)
- **Data**: Cached recommendations, analytics, search results
- **Purpose**: Performance optimization
- **Access**: Via redis-py client

## 🔧 Key Design Patterns

### 1. Repository Pattern
- Abstracts data access logic
- Enables easy testing with mock repositories
- Centralizes database queries

### 2. Service Layer Pattern
- Encapsulates business logic
- Coordinates multiple repositories
- Handles complex operations

### 3. Dependency Injection
- FastAPI's built-in dependency system
- Database session management
- Service instantiation

### 4. Schema Validation
- Pydantic models for request/response validation
- Type safety throughout the application
- Automatic API documentation

## 🧪 Testing Strategy

### Test Types
1. **Unit Tests**: Individual function/method testing
2. **Integration Tests**: Service interaction testing
3. **API Tests**: Endpoint behavior testing
4. **Database Tests**: Repository functionality testing

### Test Structure
- `conftest.py`: Shared fixtures and configuration
- Test files mirror source structure
- Isolated test database for each test
- Mock external services (Neo4j, Redis)

## 🚀 Deployment Considerations

### Environment Configuration
- Development: Local with Docker
- Staging: Container orchestration
- Production: Managed cloud services

### Scaling Points
- API layer: Horizontal scaling with load balancer
- Database: Read replicas, connection pooling
- Cache: Redis cluster for high availability
- Knowledge Graph: Neo4j clustering

## 📈 Performance Features

### Caching Strategy
- **L1**: Application-level caching (in-memory)
- **L2**: Redis distributed cache
- **TTL**: Time-based cache expiration
- **Invalidation**: Smart cache invalidation

### Database Optimization
- Indexed columns for frequent queries
- Connection pooling
- Query optimization
- Async/await support

### API Performance
- Response compression
- Rate limiting
- Request/response middleware
- Async request handling

## 🔒 Security Considerations

### Current Implementation
- Input validation with Pydantic
- SQL injection prevention via ORM
- Environment-based configuration

### Future Enhancements
- JWT authentication
- Role-based authorization
- API key management
- Request signing

## 📝 Development Guidelines

### Code Style
- PEP 8 compliance
- Type hints throughout
- Docstrings for public methods
- Meaningful variable names

### Git Workflow
- Feature branches
- Descriptive commit messages
- Pull request reviews
- Automated testing

### Documentation
- API documentation via OpenAPI/Swagger
- Code comments for complex logic
- README files for setup instructions
- Architecture documentation (this file)

## 🔄 Future Enhancements

### Planned Features
1. Authentication and authorization system
2. Real-time notifications (WebSocket)
3. Advanced ML recommendation algorithms
4. API rate limiting and throttling
5. Comprehensive monitoring and logging
6. Multi-tenant support
7. GraphQL API endpoint
8. Background job processing (Celery)

### Architectural Improvements
1. Event-driven architecture
2. Microservices decomposition
3. CQRS pattern implementation
4. Domain-driven design principles
5. Advanced caching strategies
6. Circuit breaker pattern
7. Service mesh integration