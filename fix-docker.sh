#!/bin/bash

echo "🔧 Fixing Docker Setup for Vision Dashboard"
echo ""

# Clean up any existing containers
echo "1️⃣ Cleaning up existing containers..."
docker compose down 2>/dev/null

echo "2️⃣ Building fresh Docker image..."
docker compose build --no-cache

echo "3️⃣ Starting with port 5099..."
PORT=5099 docker compose up -d

# Wait a moment
sleep 5

echo "4️⃣ Checking container status..."
if docker ps | grep -q "vision-dashboard"; then
    echo "✅ Container is running!"
    echo "🌐 Access at: http://localhost:5099"
    
    # Test the connection with timeout
    echo "5️⃣ Testing connection..."
    if timeout 10 curl -f http://localhost:5099/api/health >/dev/null 2>&1; then
        echo "✅ Application is responding!"
    else
        echo "⏳ Application starting up... (may take up to 30 seconds)"
        echo "💡 Try manually: curl http://localhost:5099/api/health"
    fi
else
    echo "❌ Container failed to start. Logs:"
    docker logs vision-dashboard 2>/dev/null || echo "No logs available"
fi