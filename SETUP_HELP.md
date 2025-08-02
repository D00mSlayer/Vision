# Quick Setup Help

## Fix for Missing Dependencies Issue

You're getting a `ModuleNotFoundError: No module named 'pyodbc'` error. Here's how to fix it:

### Option 1: Install Dependencies First
```bash
# Install the missing dependencies
pip3 install --user flask pyyaml requests pyodbc pymssql gunicorn

# OR if you have admin access:
pip3 install flask pyyaml requests pyodbc pymssql gunicorn
```

### Option 2: Use Custom Port (5099 as you wanted)
```bash
# Set your custom port in .env file
echo "PORT=5099" >> .env

# Then run the deployment script
./deploy-simple.sh
```

### Option 3: Quick Manual Start
```bash
# Install dependencies
pip3 install --user flask pyyaml requests pymssql gunicorn

# Set environment variables
export SESSION_SECRET="your-secure-key-here"
export PORT=5099

# Start the application directly
gunicorn --bind 0.0.0.0:5099 --workers 1 main:app
```

## For Docker Deployment with Custom Port

```bash
# Set port in environment
export PORT=5099

# Run docker compose
docker compose up -d
```

## Note about pyodbc

If `pyodbc` installation fails (common on some systems), the application will fall back to `pymssql` which should work fine. The dual-driver support was built exactly for this scenario.

## Quick Test

After fixing dependencies, test the application:
```bash
curl http://localhost:5099/api/health
```

You should see a JSON response indicating the health status.

## Access the Application

Once running successfully:
- **Main Dashboard**: http://localhost:5099
- **Monitor View**: Click "Switch to Monitor View" button in the main dashboard
- **Health API**: http://localhost:5099/api/health
- **Environment API**: http://localhost:5099/api/environments