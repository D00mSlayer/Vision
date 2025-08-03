# Vision - Environment Information Dashboard

A simple web dashboard for monitoring product environments and health status.

## Quick Start

```bash
# 1. Install dependencies
poetry install --no-root

# 2. Start the app
poetry run python main.py
```

Open your browser to: http://localhost:5000

That's it! The app monitors your environments automatically.

## What the files do:
- **app.py** = The Flask web application (creates the website)
- **main.py** = Startup script (runs app.py)
- **data/environments.yaml** = Your environment configuration

## Change the port:
```bash
echo "PORT=5099" > .env
poetry run python main.py
```

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
poetry run python main.py
```

**If you get import errors:**
Make sure you installed the dependencies with Poetry:
```bash
poetry install
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

## Development

**Install development dependencies:**
```bash
poetry install --with dev
```

**Format code:**
```bash
poetry run black .
```

**Lint code:**
```bash
poetry run flake8 .
```

**Run tests:**
```bash
poetry run pytest
```