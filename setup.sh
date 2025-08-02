#!/bin/bash

# Vision Dashboard Setup Script
# Simple setup for environments that already have dependencies

echo "🚀 Setting up Vision Dashboard"
echo ""

# Create logs directory
mkdir -p logs

# Check if dependencies are available
echo "📚 Checking dependencies..."
python3 -c "import flask, yaml, requests, pymssql" 2>/dev/null && echo "✅ All dependencies available" || echo "❌ Some dependencies missing - install with: pip install flask pyyaml requests pymssql gunicorn"

# Set default environment variables
export PORT=${PORT:-5000}
export SESSION_SECRET=${SESSION_SECRET:-vision-dev-secret-change-in-production}
export FLASK_ENV=${FLASK_ENV:-production}
export FLASK_DEBUG=${FLASK_DEBUG:-false}

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To start the application:"
echo "   ./run.sh"
echo ""
echo "🔧 To use a custom port:"
echo "   export PORT=5099"
echo "   ./run.sh"
echo ""
echo "📝 To edit environment data:"
echo "   Edit data/environments.yaml and refresh your browser"
echo ""
echo "🛑 To stop the application:"
echo "   Press Ctrl+C"