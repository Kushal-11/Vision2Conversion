# Personalized Marketing Backend

AI-powered personalized marketing system with knowledge graphs for generating personalized emails and vision boards.

## Quick Start

1. **Clone and setup environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start databases:**
```bash
docker-compose up -d
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## Project Structure

```
app/
├── api/v1/          # API endpoints
├── core/            # Configuration and settings
├── models/          # Data models
├── services/        # Business logic services
└── main.py          # FastAPI application
```

## External Services Setup

For production deployment, sign up for:
- Neo4j AuraDB (https://neo4j.com/cloud/aura/) - Free tier available
- Optional: Redis Cloud, PostgreSQL hosting

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
isort app/
```