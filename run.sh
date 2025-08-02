#!/bin/bash

# Vision Dashboard Run Script
# Simple script to start the application

set -e

# Set environment variables
export PORT=${PORT:-5000}
export SESSION_SECRET=${SESSION_SECRET:-vision-dev-secret-change-in-production}
export FLASK_ENV=${FLASK_ENV:-production}
export FLASK_DEBUG=${FLASK_DEBUG:-false}

echo "🚀 Starting Vision Dashboard on port $PORT"
echo "🌐 Access at: http://localhost:$PORT"
echo "📊 Health API: http://localhost:$PORT/api/health"
echo "📋 Environment API: http://localhost:$PORT/api/environments"
echo ""
echo "💡 Edit data/environments.yaml for live configuration updates!"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start the application
python main.py