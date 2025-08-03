# Vision - Environment Information Dashboard

A simple web dashboard for monitoring product environments and health status.

## Quick Start

**Step 1: Install Python dependencies**
```bash
pip install flask pyyaml requests pymssql
```

**Step 2: Set your port in .env file**
```bash
echo "PORT=5099" > .env
```

**Step 3: Run the application**

**Option A: Using python main.py (Recommended - better Ctrl+C handling)**
```bash
python main.py
```

**Option B: Using flask run**
```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5099
```
*Note: flask run may not respond to Ctrl+C properly. Use python main.py for better control.*

**Step 4: Open your browser**
Go to: http://localhost:5099

That's it! The app will start monitoring your environments automatically.

## What This App Does

- Shows health status of your product environments
- Monitors microservices and databases
- Displays everything in a clean web interface
- Updates health status automatically every 30 seconds

## Configuration

Edit `data/environments.yaml` to add your own environments. Changes take effect immediately when you refresh the browser.

## Troubleshooting

**If port 5099 is busy:**
```bash
echo "PORT=8080" > .env
python main.py
```

**If you get import errors:**
Make sure you installed the dependencies:
```bash
pip install flask pyyaml requests pymssql python-dotenv
```

**If Ctrl+C doesn't stop the app:**
Kill the process manually:
```bash
pkill -f "python main.py"
# or find the process ID and kill it
ps aux | grep python
kill [PID]
```

**If health checks fail:**
This is normal - the app tries to connect to example servers that don't exist. Replace the URLs in `data/environments.yaml` with your real servers.