#!/bin/bash

# Simple Docker runner for Vision Dashboard
# This script sets up and runs the Vision app with Docker

# Set default port if not provided
PORT=${PORT:-5099}

echo "🚀 Starting Vision Dashboard on port $PORT"
echo "📝 Edit data/environments.yaml for live configuration updates"
echo ""

# Export the port for docker-compose
export PORT=$PORT

# Run docker compose
if docker compose up -d; then
    echo ""
    echo "✅ Vision Dashboard is starting up..."
    
    # Wait a moment for the container to start
    sleep 3
    
    # Check if container is actually running
    if docker ps | grep -q "vision-dashboard"; then
        echo "✅ Container is running successfully"
    else
        echo "❌ Container failed to start. Checking logs..."
        docker logs vision-dashboard 2>/dev/null || echo "No container logs available"
        echo ""
        echo "Try rebuilding with: docker compose build --no-cache"
        exit 1
    fi
else
    echo "❌ Failed to start containers"
    exit 1
fi
echo "🌐 Access at: http://localhost:$PORT"
echo "📊 Health API: http://localhost:$PORT/api/health"
echo "📋 Environment API: http://localhost:$PORT/api/environments"
echo ""
echo "🔄 To see logs: docker compose logs -f"
echo "🛑 To stop: docker compose down"
echo ""
echo "💡 Edit data/environments.yaml and refresh browser for live updates!"