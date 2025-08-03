# Vision - Environment Information Dashboard

A simple web dashboard for monitoring product environments and health status.

## Quick Start

**Step 1: Requirements**
- Python 3.9 or higher
- Poetry (install with: `curl -sSL https://install.python-poetry.org | python3 -`)

**Step 2: Install dependencies with Poetry**
```bash
poetry install
```

**Step 3: Set your port in .env file**
```bash
echo "PORT=5099" > .env
```

**Step 4: Run the application**

**Option A: Using Poetry with Python (Recommended)**
```bash
poetry run python main.py
```

**Option B: Using Poetry shell**
```bash
poetry shell
python main.py
```

**Option C: Using Flask directly**
```bash
poetry shell
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5099
```

**Step 5: Open your browser**
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