#!/bin/bash

# Vision Dashboard Deployment Script
# This script simplifies deployment for your company servers

set -e

echo "🚀 Vision Dashboard Deployment Script"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate a secure session secret
    SESSION_SECRET=$(openssl rand -hex 32)
    sed -i "s/your-super-secure-session-key-here-minimum-32-chars/$SESSION_SECRET/" .env
    
    echo "✅ .env file created with secure session key"
    echo "   Please review and update .env file with your specific configuration"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

# Check if environment data exists
if [ ! -f data/environments.yaml ]; then
    echo "⚠️  Warning: data/environments.yaml not found"
    echo "   Please create your environment configuration file"
    echo "   You can use the sample data or create your own"
fi

# Pull latest images (if building from registry)
echo "📦 Building Vision Dashboard..."
docker-compose build

# Start the application
echo "🚀 Starting Vision Dashboard..."
docker-compose up -d

# Wait for application to be ready
echo "⏳ Waiting for application to start..."
sleep 10

# Check if application is running
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Vision Dashboard is running successfully!"
    echo ""
    echo "🌐 Access the application at: http://localhost:5000"
    echo "📊 Monitor view at: http://localhost:5000 (click 'Switch to Monitor View')"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop app:  docker-compose down"
    echo "   Restart:   docker-compose restart"
    echo "   Update:    git pull && docker-compose build && docker-compose up -d"
else
    echo "❌ Application failed to start properly"
    echo "📋 Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"