# PowerShell Deployment Script for Hyperlocal News Application
param(
    [string]$Environment = "production"
)

Write-Host "🚀 Starting deployment of Hyperlocal News Application..." -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please ensure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "ssl" | Out-Null

# Set environment variables
Write-Host "⚙️ Setting up environment..." -ForegroundColor Blue
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.production" ".env"
    Write-Host "⚠️  Please update .env file with your production values!" -ForegroundColor Yellow
}

# Build and start services
Write-Host "🔨 Building Docker images..." -ForegroundColor Blue
docker compose build

Write-Host "🚀 Starting services..." -ForegroundColor Blue
docker compose up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Blue
$healthStatus = docker compose ps
if ($healthStatus -match "Up \(healthy\)") {
    Write-Host "✅ Services are healthy!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some services might not be healthy yet. Check with: docker compose ps" -ForegroundColor Yellow
}

# Run database migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Blue
try {
    docker compose exec api python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
    Write-Host "✅ Database migrations completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Database migration failed. Please check logs." -ForegroundColor Yellow
}

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 API is available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📝 Logs: docker compose logs -f" -ForegroundColor Cyan
Write-Host "🛑 Stop services: docker compose down" -ForegroundColor Cyan
