-- PostgreSQL Database Setup for Hyperlocal News Application
-- Run this script in PostgreSQL to create the database and initial setup

-- Create the database (run this as postgres user)
CREATE DATABASE news_platform;

-- Create user for the application (optional, if you want a dedicated user)
-- CREATE USER news_app_user WITH PASSWORD 'password';
-- GRANT ALL PRIVILEGES ON DATABASE news_platform TO news_app_user;

-- Connect to the news_platform database and create extensions
\c news_platform;

-- Create extensions needed for the application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- For location-based features

-- Create schema (optional, if you want to organize tables)
-- CREATE SCHEMA IF NOT EXISTS news_app;
-- SET search_path TO news_app, public;

-- Grant permissions (if using dedicated user)
-- GRANT ALL ON SCHEMA public TO news_app_user;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO news_app_user;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO news_app_user;

-- Verify database creation
\l

-- Show current database
SELECT current_database();

-- Show extensions
\dx
