# Environment Setup Guide

This guide will help you set up the environment variables needed for the Personalized Marketing Backend.

## Quick Setup

1. **Run the environment setup script:**
   ```bash
   make env-setup
   ```
   This will create a `.env` file with secure defaults.

2. **Start the services:**
   ```bash
   make docker-up
   ```

3. **Set up the database:**
   ```bash
   make setup
   ```

4. **Start the development server:**
   ```bash
   make dev
   ```

## Manual Setup

If you prefer to set up environment variables manually:

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your preferred values.

## Environment Variables Explained

### 🗄️ Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_SERVER` | PostgreSQL server hostname | `localhost` | ✅ |
| `POSTGRES_USER` | Database username | `postgres` | ✅ |
| `POSTGRES_PASSWORD` | Database password | `password` | ✅ |
| `POSTGRES_DB` | Database name | `marketing_db` | ✅ |
| `POSTGRES_PORT` | Database port | `5433` | ✅ |

### 🕸️ Neo4j Configuration (Knowledge Graph)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` | ✅ |
| `NEO4J_USER` | Neo4j username | `neo4j` | ✅ |
| `NEO4J_PASSWORD` | Neo4j password | `password` | ✅ |

### 🔴 Redis Configuration (Caching)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_HOST` | Redis server hostname | `localhost` | ✅ |
| `REDIS_PORT` | Redis port | `6380` | ✅ |
| `REDIS_DB` | Redis database number | `0` | ✅ |
| `REDIS_PASSWORD` | Redis password | (empty) | ❌ |

### 🔐 Security Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT secret key | (auto-generated) | ✅ |
| `ALGORITHM` | JWT algorithm | `HS256` | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` | ✅ |

### ⚙️ API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_V1_STR` | API version prefix | `/api/v1` | ✅ |
| `PROJECT_NAME` | Project name | `Personalized Marketing Backend` | ✅ |
| `DEBUG` | Enable debug mode | `true` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` | ❌ |

### 📧 External Services (Optional)

These are optional and only needed if you want to integrate with external services:

| Variable | Description | Required |
|----------|-------------|----------|
| `SENDGRID_API_KEY` | SendGrid API key for email sending | ❌ |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3/other services | ❌ |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | ❌ |
| `S3_BUCKET_NAME` | S3 bucket for file storage | ❌ |

### 📊 Monitoring (Optional)

| Variable | Description | Required |
|----------|-------------|----------|
| `SENTRY_DSN` | Sentry DSN for error tracking | ❌ |
| `DATADOG_API_KEY` | Datadog API key for metrics | ❌ |

## Different Environment Configurations

### Development Environment

For local development, the default values should work with the provided Docker setup:

```bash
# Use the defaults in .env.example
cp .env.example .env
```

### Production Environment

For production, you should:

1. **Generate a strong secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

2. **Use secure passwords** for all services

3. **Set appropriate hosts** (not localhost)

4. **Disable debug mode:**
   ```
   DEBUG=false
   LOG_LEVEL=WARNING
   ```

5. **Configure external services** if needed

### Docker Environment

If running everything in Docker, adjust the hosts:

```env
POSTGRES_SERVER=postgres
NEO4J_URI=bolt://neo4j:7687
REDIS_HOST=redis
```

## Checking Your Setup

1. **Check if all required variables are set:**
   ```bash
   make env-check
   ```

2. **View the environment guide:**
   ```bash
   make env-guide
   ```

3. **Test database connection:**
   ```bash
   make check-db
   ```

## Troubleshooting

### Common Issues

1. **"Connection refused" errors:**
   - Make sure Docker services are running: `make docker-up`
   - Check if ports are correct in your `.env` file

2. **"Authentication failed" errors:**
   - Check if passwords match between `.env` and `docker-compose.yml`
   - For Neo4j, the default password is `password`

3. **"Permission denied" errors:**
   - Make sure your user has permission to access Docker
   - Try running with `sudo` if needed

4. **Import errors:**
   - Make sure you've installed dependencies: `make install`
   - Check if you're in the right Python environment

### Service-Specific Issues

**PostgreSQL:**
- Default port 5433 (not standard 5432) to avoid conflicts
- Username: `postgres`, Password: `password`

**Neo4j:**
- Default port 7687 for Bolt protocol
- Web interface at http://localhost:7474
- Username: `neo4j`, Password: `password`

**Redis:**
- Default port 6380 (not standard 6379) to avoid conflicts
- No authentication by default

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit `.env` files** to version control
2. **Change default passwords** in production
3. **Use strong secret keys** (auto-generated is recommended)
4. **Restrict network access** in production
5. **Enable authentication** on all services in production
6. **Use HTTPS** in production
7. **Regularly rotate secrets**

## Getting Help

If you encounter issues:

1. Check the logs: `make logs-api`, `make logs-db`, etc.
2. Verify services are running: `make status`
3. Check the troubleshooting section above
4. Review the application logs for specific error messages

## Next Steps

After setting up your environment:

1. **Start development:** `make dev`
2. **Access the API docs:** http://localhost:8000/docs
3. **Explore the endpoints** using the interactive documentation
4. **Run tests:** `make test`
5. **Check the analytics dashboard** via the API endpoints