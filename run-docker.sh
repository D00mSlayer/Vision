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
docker compose up -d

echo ""
echo "✅ Vision Dashboard is starting up..."
echo "🌐 Access at: http://localhost:$PORT"
echo "📊 Health API: http://localhost:$PORT/api/health"
echo "📋 Environment API: http://localhost:$PORT/api/environments"
echo ""
echo "🔄 To see logs: docker compose logs -f"
echo "🛑 To stop: docker compose down"
echo ""
echo "💡 Edit data/environments.yaml and refresh browser for live updates!"