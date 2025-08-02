#!/bin/bash

echo "🔍 Debugging Docker Setup for Vision Dashboard"
echo ""

echo "1️⃣ Checking if Docker container is running..."
docker ps | grep vision

echo ""
echo "2️⃣ Checking Docker container logs..."
docker logs vision-dashboard --tail 10

echo ""
echo "3️⃣ Testing internal health check..."
PORT_IN_CONTAINER=$(docker exec vision-dashboard printenv PORT 2>/dev/null || echo "5000")
docker exec vision-dashboard curl -f http://localhost:${PORT_IN_CONTAINER}/api/health 2>/dev/null && echo "✅ Internal health check passed" || echo "❌ Internal health check failed"

echo ""
echo "4️⃣ Checking port mapping..."
docker port vision-dashboard

echo ""
echo "5️⃣ Testing external connection..."
EXTERNAL_PORT=${PORT:-5099}
curl -f http://localhost:${EXTERNAL_PORT}/api/health 2>/dev/null && echo "✅ External connection works" || echo "❌ External connection failed"

echo ""
echo "💡 If external connection failed, try:"
echo "   docker compose down"
echo "   PORT=${PORT:-5099} docker compose up -d"