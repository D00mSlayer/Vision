import os
import yaml
import logging
import requests
import pyodbc
import re
import threading
import time
from flask import Flask, render_template, jsonify, request
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

IS_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
PORT = int(os.getenv('PORT', 8080))
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))
DB_TIMEOUT = int(os.getenv('DB_TIMEOUT', 10))
URL_TIMEOUT = int(os.getenv('URL_TIMEOUT', 10))
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 10))
MONITOR_SCROLL_INTERVAL_SECONDS = int(os.getenv('MONITOR_SCROLL_INTERVAL_SECONDS', 8))
MONITOR_SCROLL_PERCENTAGE = float(os.getenv('MONITOR_SCROLL_PERCENTAGE', 0.8))
SQL_EDITOR_RESULT_LIMIT = int(os.getenv('SQL_EDITOR_RESULT_LIMIT', 100))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

health_status = {}
health_status_lock = threading.Lock()

def load_yaml_data(file_path):
    """Generic function to load a YAML file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        app.logger.error(f"YAML file not found at: {file_path}")
    except Exception as e:
        app.logger.error(f"Error parsing YAML file {file_path}: {e}")
    return None

def check_url_health(url):
    """Checks a single URL endpoint."""
    try:
        response = requests.get(url, timeout=URL_TIMEOUT, headers={'User-Agent': 'VisionDashboard-HealthCheck/1.0'})
        return response.status_code >= 200 and response.status_code < 400
    except requests.RequestException as e:
        app.logger.debug(f"URL check failed for {url}: {e}")
        return False

def check_database_health(db_config):
    """Checks a single MS-SQL database connection using pyodbc and ODBC Driver 18."""
    driver = "{ODBC Driver 18 for SQL Server}"
    
    connection_string = (
        f"DRIVER={driver};"
        f"SERVER={db_config['host']},{db_config['port']};"
        f"DATABASE={db_config['database_name']};"
        f"UID={db_config['username']};"
        f"PWD={db_config['password']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout={DB_TIMEOUT};"
    )

    try:
        with pyodbc.connect(connection_string) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except pyodbc.Error as e:
        app.logger.debug(f"pyodbc DB check failed for {db_config['host']}: {e}")
        return False
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during pyodbc check for {db_config['host']}: {e}")
        return False

def run_all_health_checks():
    """Gathers all services from YAML, de-duplicates them, and runs checks in parallel."""
    app.logger.info("Starting a new health check cycle...")
    environment_data = load_yaml_data('data/environments.yaml')
    if not environment_data or 'product_versions' not in environment_data:
        app.logger.warning("No product versions found in environments data. Skipping health checks.")
        return

    unique_checks = {}
    for product in environment_data.get('product_versions', []):
        for env in product.get('environments', []):
            if env.get('url'):
                key = f"env_{env['url']}"
                if key not in unique_checks:
                    unique_checks[key] = ('url', env['url'])
            
            for ms in env.get('microservices', []):
                if ms.get('server_url') and ms.get('port'):
                    key = f"ms_{ms['server_url']}"
                    if key not in unique_checks:
                        parsed = urlparse(ms['server_url'])
                        health_url = f"{parsed.scheme}://{parsed.hostname}:{ms['port']}{parsed.path}"
                        unique_checks[key] = ('url', health_url)
            
            for db in env.get('databases', []):
                key = f"db_{db['host']}:{db['port']}/{db['database_name']}"
                if key not in unique_checks:
                    unique_checks[key] = ('database', db)

    if not unique_checks:
        app.logger.info("No unique services found to check.")
        return

    latest_status = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_key = {}
        for key, (check_type, data) in unique_checks.items():
            if check_type == 'url':
                future = executor.submit(check_url_health, data)
            elif check_type == 'database':
                future = executor.submit(check_database_health, data)
            future_to_key[future] = key

        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                latest_status[key] = future.result()
            except Exception as exc:
                app.logger.error(f"Health check for '{key}' generated an exception: {exc}")
                latest_status[key] = False

    with health_status_lock:
        health_status.clear()
        health_status.update(latest_status)
    
    app.logger.info(f"Health check cycle complete. Checked {len(latest_status)} unique services.")

def health_check_worker():
    """Background worker to run health checks periodically."""
    app.logger.info("Background health check worker started.")
    run_all_health_checks()
    
    while True:
        time.sleep(HEALTH_CHECK_INTERVAL)
        run_all_health_checks()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Provides a single source of truth for the dashboard."""
    environment_data = load_yaml_data('data/environments.yaml')
    with health_status_lock:
        current_health = health_status.copy()

    return jsonify({
        'environments': environment_data or {"product_versions": []},
        'health': current_health
    })

@app.route('/api/bookmarks')
def get_bookmarks():
    data = load_yaml_data('data/bookmarks.yaml')
    return jsonify(data or {"bookmarks": []})

@app.route('/api/config')
def get_app_config():
    return jsonify({
        'healthCheckIntervalMs': HEALTH_CHECK_INTERVAL * 1000,
        'monitorScrollIntervalMs': MONITOR_SCROLL_INTERVAL_SECONDS * 1000,
        'monitorScrollPercentage': MONITOR_SCROLL_PERCENTAGE
    })

@app.route('/api/db/execute', methods=['POST'])
def execute_sql_query():
    """Executes a read-only SQL query, automatically adding NOLOCK hints."""
    data = request.get_json()
    db_config = data.get('db_config')
    query = data.get('query', '').strip()

    if not query.upper().startswith('SELECT'):
        return jsonify({'success': False, 'error': 'Only SELECT statements are allowed.'}), 400

    if not db_config:
        return jsonify({'success': False, 'error': 'Database configuration is missing.'}), 400

    nolock_pattern = re.compile(
        r'(\bFROM\b|\bJOIN\b)\s+([a-zA-Z0-9_\[\].]+)\b(?!\s+WITH\s*\()',
        re.IGNORECASE | re.MULTILINE
    )
    query_with_nolock = nolock_pattern.sub(r'\1 \2 WITH (NOLOCK)', query)
    app.logger.info(f"Augmented SQL Query: {query_with_nolock}")

    driver = "{ODBC Driver 18 for SQL Server}"
    connection_string = (
        f"DRIVER={driver};"
        f"SERVER={db_config['host']},{db_config['port']};"
        f"DATABASE={db_config['database_name']};"
        f"UID={db_config['username']};"
        f"PWD={db_config['password']};"
        f"Encrypt=yes;TrustServerCertificate=yes;"
        f"Connection Timeout={DB_TIMEOUT};"
    )

    try:
        with pyodbc.connect(connection_string, autocommit=True) as connection:
            cursor = connection.cursor()
            cursor.execute(query_with_nolock)
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                all_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                total_row_count = len(all_rows)
                limited_rows = all_rows[:SQL_EDITOR_RESULT_LIMIT]
            else:
                columns, limited_rows, total_row_count = [], [], cursor.rowcount

        return jsonify({
            'success': True, 
            'columns': columns, 
            'rows': limited_rows, 
            'rowCount': total_row_count,
            'limit': SQL_EDITOR_RESULT_LIMIT,
            'executedQuery': query_with_nolock
        })

    except pyodbc.Error as e:
        return jsonify({'success': False, 'error': str(e), 'executedQuery': query_with_nolock})
    except Exception as e:
        return jsonify({'success': False, 'error': f"An unexpected error occurred: {e}"}), 500



if __name__ == '__main__':
    health_thread = threading.Thread(target=health_check_worker, daemon=True)
    health_thread.start()
    
    app.run(debug=True, use_reloader=False)
