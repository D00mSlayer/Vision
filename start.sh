#!/bin/bash
# Ensure this script maintains executable permissions
chmod +x "$0" 2>/dev/null || true

# Vision Dashboard - Complete Setup and Run Script
# This script handles everything: prerequisites, virtual environment, dependencies, and startup

set -e  # Exit on any error

echo "🚀 Vision Dashboard - Complete Setup & Start"
echo "=============================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0"
}

# Function to compare version numbers
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C 2>/dev/null
}

echo "📋 Checking Prerequisites..."

# Check Python 3
if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ using:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(get_python_version)
if ! version_ge "$PYTHON_VERSION" "3.8"; then
    echo "❌ Python 3.8+ required, found $PYTHON_VERSION"
    echo "Please upgrade Python 3 to version 3.8 or higher"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check pip
if ! command_exists pip3; then
    echo "❌ pip3 is not installed"
    echo "Please install pip3 using:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3-pip"
    exit 1
fi

echo "✅ pip3 found"

# Check if python3-venv is available (required on some distributions)
if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "❌ python3-venv module not available"
    echo "Please install python3-venv using:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3-venv"
    exit 1
fi

echo "✅ python3-venv available"

# Check for system dependencies needed for MS SQL drivers
echo ""
echo "📦 Checking System Dependencies for MS SQL..."
MISSING_DEPS=()

# Check for required system packages
if ! command_exists gcc; then
    MISSING_DEPS+=("build-essential" "gcc")
fi

if ! ldconfig -p | grep -q unixodbc; then
    MISSING_DEPS+=("unixodbc-dev")
fi

if ! ldconfig -p | grep -q freetds; then
    MISSING_DEPS+=("freetds-dev")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Some system dependencies for MS SQL drivers are missing:"
    printf '   - %s\n' "${MISSING_DEPS[@]}"
    echo ""
    echo "Install them using:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install build-essential unixodbc-dev freetds-dev"
    echo "  CentOS/RHEL:   sudo yum groupinstall 'Development Tools' && sudo yum install unixODBC-devel freetds-devel"
    echo "  Fedora:        sudo dnf groupinstall 'Development Tools' && sudo dnf install unixODBC-devel freetds-devel"
    echo ""
    echo "MS SQL database health checks may not work without these dependencies."
    echo "Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please install the required dependencies and try again."
        exit 1
    fi
else
    echo "✅ System dependencies for MS SQL found"
fi

echo ""
echo "🔧 Setting up Virtual Environment..."

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "📁 Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "📚 Installing Python Dependencies..."
echo "This may take a few minutes..."

pip install flask>=2.3.0
pip install pyyaml>=6.0
pip install requests>=2.31.0
pip install gunicorn>=21.0.0
pip install python-dotenv>=1.0.0

# Try to install MS SQL drivers
echo ""
echo "🔧 Installing MS SQL Drivers..."
if pip install pymssql>=2.2.0; then
    echo "✅ pymssql installed successfully"
else
    echo "⚠️  Failed to install pymssql (MS SQL driver)"
    echo "Database health checks will not work for MS SQL databases"
fi

# Try to install pyodbc as backup
if pip install pyodbc>=4.0.0; then
    echo "✅ pyodbc installed successfully"
else
    echo "⚠️  Failed to install pyodbc (alternative MS SQL driver)"
fi

# Create logs directory
echo ""
echo "📂 Creating logs directory..."
mkdir -p logs

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    set -a  # Automatically export all variables
    source .env
    set +a  # Stop auto-exporting
fi

# Set environment variables with defaults
export PORT=${PORT:-5000}
export SESSION_SECRET=${SESSION_SECRET:-vision-dev-secret-change-in-production}
export FLASK_ENV=${FLASK_ENV:-production}
export FLASK_DEBUG=${FLASK_DEBUG:-false}

echo "🔧 Configuration:"
echo "   PORT: $PORT"
echo "   FLASK_ENV: $FLASK_ENV"
echo "   FLASK_DEBUG: $FLASK_DEBUG"

# Check if port is available using Python socket binding
echo ""
echo "🔍 Checking port availability..."
python3 -c "
import socket
import sys

def check_port_available(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False

port = int('$PORT')
if not check_port_available(port):
    print(f'❌ Error: Port {port} is already in use!')
    print('')
    print('Solutions:')
    print('1. Use a different port: PORT=5099 ./start.sh')
    print('2. Kill the process using port', port)
    print('3. Edit .env file to use a different port')
    print('')
    sys.exit(1)
else:
    print(f'✅ Port {port} is available')
"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🚀 Starting Vision Dashboard..."
echo "================================"
echo "🌐 Access at: http://localhost:$PORT"
echo "📊 Health API: http://localhost:$PORT/api/health"
echo "📋 Environment API: http://localhost:$PORT/api/environments"
echo ""
echo "💡 Edit data/environments.yaml for live configuration updates!"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start the application with virtual environment activated
echo "📡 Starting Flask application..."
source venv/bin/activate

# Handle Ctrl+C gracefully
trap 'echo ""; echo "🛑 Stopping Vision Dashboard..."; kill $PID 2>/dev/null; exit 0' INT

# Start Python in background and capture PID
python main.py &
PID=$!

# Wait for the process and handle signals
echo "🔄 Vision Dashboard running (PID: $PID)"
echo "🛑 Press Ctrl+C to stop"
wait $PID