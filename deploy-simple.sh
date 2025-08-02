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

# Install dependencies (only if pip is available and this isn't Replit)
if command -v pip &> /dev/null && [ ! -f .replit ]; then
    echo "📦 Installing Python dependencies..."
    pip install flask pyyaml requests pyodbc pymssql gunicorn || {
        echo "⚠️  Failed to install some dependencies. This is normal if some are already installed."
        echo "   Required packages: flask, pyyaml, requests, pyodbc, pymssql, gunicorn"
    }
else
    echo "✅ Dependencies assumed to be managed by environment (Replit/container)"
fi

# Set environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
fi

# Start the application
echo "🚀 Starting Vision Dashboard..."

if command -v gunicorn &> /dev/null; then
    echo "   Using Gunicorn server..."
    gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 main:app &
    APP_PID=$!
else
    echo "   Using Flask development server..."
    python3 main.py &
    APP_PID=$!
fi

# Wait for application to be ready
echo "⏳ Waiting for application to start..."
sleep 5

# Check if application is running
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Vision Dashboard is running successfully!"
    echo ""
    echo "🌐 Access the application at: http://localhost:5000"
    echo "📊 Monitor view at: http://localhost:5000 (click 'Switch to Monitor View')"
    echo ""
    echo "📋 Useful commands:"
    echo "   Stop app:  kill $APP_PID"
    echo "   Check logs: tail -f logs/app.log"
    echo "   View process: ps aux | grep python"
elif ps -p $APP_PID > /dev/null; then
    echo "✅ Application started (PID: $APP_PID)"
    echo "🌐 Access the application at: http://localhost:5000"
    echo "⏳ Application may still be initializing, please wait a moment"
else
    echo "❌ Application failed to start properly"
    echo "📋 Check for errors in the terminal output above"
    exit 1
fi

echo ""
echo "🎉 Simple deployment completed successfully!"
echo "💡 For production deployment with Docker, use './deploy.sh' instead"