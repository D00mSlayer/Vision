# Vision - Environment Information Dashboard

A simple web dashboard for monitoring product environments and health status.

## Quick Start

**Step 1: Install Python dependencies**
```bash
pip install flask pyyaml requests pymssql
```

**Step 2: Run the application**
```bash
python run-local.py
```

**Step 3: Open your browser**
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
PORT=8080 python run-local.py
```

**If you get import errors:**
Make sure you installed the dependencies:
```bash
pip install flask pyyaml requests pymssql
```

**If health checks fail:**
This is normal - the app tries to connect to example servers that don't exist. Replace the URLs in `data/environments.yaml` with your real servers.