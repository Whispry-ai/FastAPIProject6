# Hyperlocal News Application - Real-time Deployment

A FastAPI-based hyperlocal news application with real-time features, AI-powered content generation, and location-based news delivery.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PostgreSQL (handled by Docker)
- Redis (handled by Docker)

### Local Development
```bash
# Clone and navigate to project
cd FastAPIProject6

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 📋 Services

- **API**: FastAPI application (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache & message broker (port 6379)
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled tasks
- **Nginx**: Reverse proxy (port 80/443)

## 🔧 Configuration

### Environment Variables
Copy `.env.production` to `.env` and update:
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: OAuth credentials
- `DB_PASSWORD`: Database password
- `SECRET_KEY`: Application secret
- `ALLOWED_ORIGINS`: Your frontend domains

### Database Setup
The application automatically creates tables on startup. For production:
1. Update database credentials in `.env`
2. Run migrations if needed

## 🌐 API Endpoints

- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Main API**: `http://localhost:8000`

## 🔄 Real-time Features

- WebSocket connections for live updates
- Celery tasks for background processing
- Scheduled news publishing
- Location-based content delivery

## 📊 Monitoring

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### Health Checks
```bash
# Check service status
docker-compose ps

# API health check
curl http://localhost:8000/health
```

## 🛠️ Development

### Local Setup without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL and Redis locally
# Update .env with local database URL

# Run API server
uvicorn main:app --reload

# Run Celery worker (separate terminal)
celery -A celery_worker worker --loglevel=info

# Run Celery beat (separate terminal)
celery -A celery_worker beat --loglevel=info
```

## 🔒 Security Features

- Google OAuth authentication
- Session management
- CORS protection
- Environment variable security
- Nginx SSL support (production)

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale API workers
docker-compose up -d --scale api=3

# Scale Celery workers
docker-compose up -d --scale celery_worker=2
```

### Production Optimizations
- Gunicorn WSGI server
- Nginx reverse proxy
- Redis clustering
- Database connection pooling
- SSL termination

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts**: Update ports in `docker-compose.yml`
2. **Database connection**: Check PostgreSQL service health
3. **Redis connection**: Verify Redis is running
4. **Environment variables**: Ensure `.env` is properly configured

### Reset Services
```bash
# Stop and remove containers
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

## 📝 License

Add your license information here.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
