-- Initialize database for Hyperlocal News Application
-- This script runs when PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create database if it doesn't exist
-- Note: This is handled by POSTGRES_DB environment variable in docker-compose.yml
