# Vision2Conversion - AI-Powered Personalized Marketing Platform

A comprehensive AI-powered marketing platform that converts user behavior and interests into personalized recommendations and marketing content using knowledge graphs.

## 🌟 Features

- **🧠 Knowledge Graph Engine**: Neo4j-powered recommendation system
- **📧 Personalized Email Generation**: AI-generated marketing emails with custom templates
- **🎨 Vision Board Creation**: Personalized product vision boards
- **📊 Advanced Analytics**: Real-time business intelligence and user insights
- **⚡ High-Performance Caching**: Redis-based caching for optimal performance
- **🔍 Interest Tracking**: Multi-source user interest analysis and confidence scoring
- **🚀 RESTful API**: Comprehensive API with OpenAPI documentation

## 🏗️ Architecture

```
Vision2Conversion/
├── backend/                 # Backend API server
│   ├── app/                # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kushal-11/Vision2Conversion.git
   cd Vision2Conversion/backend
   ```

2. **Set up environment:**
   ```bash
   make env-setup
   ```

3. **Start services:**
   ```bash
   make docker-up
   ```

4. **Initialize database:**
   ```bash
   make setup
   ```

5. **Run the application:**
   ```bash
   make dev
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - API Health Check: http://localhost:8000/health
   - Neo4j Browser: http://localhost:7474

## 📖 Documentation

### API Endpoints

- **Users**: `/api/v1/users/` - User management and data ingestion
- **Products**: `/api/v1/products/` - Product catalog management
- **Recommendations**: `/api/v1/recommendations/` - Personalized recommendations
- **Interests**: `/api/v1/interests/` - User interest tracking
- **Marketing**: `/api/v1/marketing/` - Email and vision board generation
- **Analytics**: `/api/v1/analytics/` - Business intelligence
- **Cache**: `/api/v1/cache/` - Cache management

### Core Services

- **Recommendation Engine**: Neo4j-based collaborative filtering
- **Marketing Automation**: Jinja2-powered email templates
- **Vision Board Generator**: Personalized product collections
- **Analytics Engine**: Real-time business metrics
- **Cache Layer**: Redis-powered performance optimization

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (Primary database)
- Neo4j (Knowledge graph database)
- Redis (Caching layer)
- SQLAlchemy (ORM)
- Alembic (Database migrations)

**AI/ML:**
- Knowledge graph algorithms
- Collaborative filtering
- Interest confidence scoring
- Personalization algorithms

**Infrastructure:**
- Docker & Docker Compose
- Pydantic (Data validation)
- Jinja2 (Template engine)
- Pytest (Testing framework)

## 📊 Key Features

### 🧠 Intelligent Recommendations
- Collaborative filtering using Neo4j knowledge graphs
- User similarity analysis
- Interest-based product matching
- Real-time recommendation scoring

### 📧 Marketing Automation
- Personalized email generation
- Multiple template types (welcome, recommendations, interest-based)
- Dynamic content insertion
- Campaign management

### 🎨 Vision Boards
- Personalized product collections
- Multiple visual themes and styles
- User interest-driven product selection
- Customizable layouts

### 📈 Advanced Analytics
- User behavior analysis
- Product performance metrics
- Revenue analytics
- Interest distribution insights
- Real-time dashboards

### ⚡ Performance
- Redis caching for sub-second response times
- Optimized database queries
- Async/await support
- Connection pooling

## 🔧 Development

### Available Commands

```bash
make help          # Show all available commands
make env-setup     # Setup environment variables
make install       # Install dependencies
make dev          # Run development server
make test         # Run test suite
make lint         # Run code linting
make format       # Format code
make docker-up    # Start all services
make docker-down  # Stop all services
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
pytest tests/test_api.py -v
pytest tests/test_recommendations.py -v
pytest tests/test_marketing.py -v
```

### Database Operations

```bash
# Run migrations
make migrate

# Seed test data
make seed

# Reset database
make reset-db
```

## 🌐 API Usage Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "profile_data": {"name": "John Doe", "age": 30}
  }'
```

### Get Personalized Recommendations
```bash
curl "http://localhost:8000/api/v1/recommendations/users/{user_id}"
```

### Generate Marketing Email
```bash
curl -X POST "http://localhost:8000/api/v1/marketing/emails/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "template_type": "personalized_recommendations",
    "recommendations_limit": 5
  }'
```

### Create Vision Board
```bash
curl -X POST "http://localhost:8000/api/v1/marketing/vision-boards/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "theme": "Tech Enthusiast",
    "product_limit": 9,
    "style": "modern"
  }'
```

## 🔒 Security

- JWT-based authentication ready (implementation pending)
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy
- Rate limiting support
- Environment-based configuration
- Secure secret management

## 🚀 Deployment

### Environment Configuration

The application supports multiple environments:

- **Development**: Local setup with Docker
- **Staging**: Pre-production testing
- **Production**: Full deployment with external services

### External Services

For production deployment, consider:
- Neo4j AuraDB (managed Neo4j)
- Redis Cloud (managed Redis)
- PostgreSQL hosting (AWS RDS, etc.)
- Container orchestration (Kubernetes, ECS)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions or support:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the setup guide in `backend/SETUP.md`

## 🏆 Acknowledgments

Built with modern Python web technologies and industry best practices for scalable, maintainable code.

---

**Vision2Conversion** - Transforming user insights into personalized experiences through AI-powered knowledge graphs.