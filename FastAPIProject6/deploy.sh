#!/bin/bash

# Deployment Script for Hyperlocal News Application
set -e

echo "🚀 Starting deployment of Hyperlocal News Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs ssl

# Set environment variables
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.production .env
    echo "⚠️  Please update .env file with your production values!"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Services are healthy!"
else
    echo "⚠️  Some services might not be healthy yet. Check with: docker-compose ps"
fi

# Run database migrations (if needed)
echo "🗄️ Running database migrations..."
docker-compose exec api python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

echo "🎉 Deployment completed successfully!"
echo "🌐 API is available at: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "📝 Logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
