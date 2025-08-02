#!/bin/bash

# Vision Dashboard Simple Deployment Script
# For environments without Docker (e.g., Replit, simple Python servers)

set -e

echo "🚀 Vision Dashboard Simple Deployment Script"
echo "============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Warning: Python version $PYTHON_VERSION detected. Python 3.11+ is recommended."
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate a secure session secret
    if command -v openssl &> /dev/null; then
        SESSION_SECRET=$(openssl rand -hex 32)
        sed -i "s/your-super-secure-session-key-here-minimum-32-chars/$SESSION_SECRET/" .env
        echo "✅ .env file created with secure session key"
    else
        echo "⚠️  .env file created. Please manually update SESSION_SECRET with a secure 32+ character key."
    fi
    
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

# Install dependencies
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install flask pyyaml requests pyodbc pymssql gunicorn || {
        echo "⚠️  Some dependencies failed to install. Trying with user installation..."
        pip3 install --user flask pyyaml requests pyodbc pymssql gunicorn || {
            echo "⚠️  Some dependencies still failed. Continuing with available packages..."
            echo "   Required packages: flask, pyyaml, requests, pyodbc, pymssql, gunicorn"
        }
    }
elif command -v pip &> /dev/null; then
    pip install flask pyyaml requests pyodbc pymssql gunicorn || {
        echo "⚠️  Some dependencies failed to install. Trying with user installation..."
        pip install --user flask pyyaml requests pyodbc pymssql gunicorn || {
            echo "⚠️  Some dependencies still failed. Continuing with available packages..."
            echo "   Required packages: flask, pyyaml, requests, pyodbc, pymssql, gunicorn"
        }
    }
else
    echo "⚠️  pip not found. Please install dependencies manually:"
    echo "   pip install flask pyyaml requests pyodbc pymssql gunicorn"
fi

# Set environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
fi

# Get port from environment or use default
PORT=${PORT:-5000}

# Start the application
echo "🚀 Starting Vision Dashboard on port $PORT..."

if command -v gunicorn &> /dev/null; then
    echo "   Using Gunicorn server..."
    gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app &
    APP_PID=$!
else
    echo "   Using Flask development server..."
    export FLASK_RUN_PORT=$PORT
    python3 main.py &
    APP_PID=$!
fi

# Wait for application to be ready
echo "⏳ Waiting for application to start..."
sleep 5

# Check if application is running
if curl -f http://localhost:$PORT/api/health > /dev/null 2>&1; then
    echo "✅ Vision Dashboard is running successfully!"
    echo ""
    echo "🌐 Access the application at: http://localhost:$PORT"
    echo "📊 Monitor view at: http://localhost:$PORT (click 'Switch to Monitor View')"
    echo ""
    echo "📋 Useful commands:"
    echo "   Stop app:  kill $APP_PID"
    echo "   Check logs: tail -f logs/app.log"
    echo "   View process: ps aux | grep python"
elif ps -p $APP_PID > /dev/null; then
    echo "✅ Application started (PID: $APP_PID)"
    echo "🌐 Access the application at: http://localhost:$PORT"
    echo "⏳ Application may still be initializing, please wait a moment"
else
    echo "❌ Application failed to start properly"
    echo "📋 Check for errors in the terminal output above"
    exit 1
fi

echo ""
echo "🎉 Simple deployment completed successfully!"
echo "💡 For production deployment with Docker, use './deploy.sh' instead"