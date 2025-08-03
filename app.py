import os
import yaml
import logging
import requests
import pyodbc
import pymssql
from flask import Flask, render_template, jsonify
from urllib.parse import urlparse
import threading
import time

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, skip loading .env files
    pass

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

# Configure Jinja2 to use different delimiters to avoid conflicts with AngularJS
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

# Global variable to store environment data and health status
environment_data = {}
health_status = {}

def load_environment_data():
    """Load environment data from YAML file"""
    global environment_data
    try:
        with open('data/environments.yaml', 'r') as file:
            environment_data = yaml.safe_load(file)
        app.logger.info("Environment data loaded successfully")
    except Exception as e:
        app.logger.error(f"Error loading environment data: {e}")
        environment_data = {"product_versions": []}

def check_url_health(url):
    """Check if a URL is reachable"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def check_database_health(host, port, database_name, username, password):
    """Check if a MS SQL database is accessible using pyodbc or pymssql"""
    
    # First try pyodbc with available drivers
    try:
        drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server", 
            "FreeTDS",
            "SQL Server"
        ]
        
        for driver in drivers:
            try:
                connection_string = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={host},{port};"
                    f"DATABASE={database_name};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"TrustServerCertificate=yes;"
                    f"Connection Timeout=5;"
                )
                connection = pyodbc.connect(connection_string)
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                connection.close()
                return True
            except pyodbc.Error:
                continue
    except Exception:
        pass
    
    # Fallback to pymssql
    try:
        connection = pymssql.connect(
            server=host,
            user=username,
            password=password,
            database=database_name,
            port=port,
            timeout=5,
            login_timeout=5
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        app.logger.debug(f"MS SQL database health check failed for {host}:{port}/{database_name}: {e}")
        return False

def update_health_status():
    """Update health status for all URLs and databases"""
    global health_status
    
    if not environment_data:
        return
    
    for product in environment_data.get('product_versions', []):
        for env in product.get('environments', []):
            env_url = env.get('url')
            if env_url:
                health_key = f"env_{env_url}"
                health_status[health_key] = check_url_health(env_url)
            
            for microservice in env.get('microservices', []):
                ms_url = microservice.get('server_url')
                if ms_url:
                    health_key = f"ms_{ms_url}"
                    health_status[health_key] = check_url_health(ms_url)
            
            for database in env.get('databases', []):
                if all(key in database for key in ['host', 'port', 'database_name', 'username', 'password']):
                    db_identifier = f"{database['host']}:{database['port']}/{database['database_name']}"
                    health_key = f"db_{db_identifier}"
                    health_status[health_key] = check_database_health(
                        database['host'],
                        database['port'],
                        database['database_name'],
                        database['username'],
                        database['password']
                    )

def health_check_worker():
    """Background worker to continuously update health status"""
    while True:
        update_health_status()
        time.sleep(30)  # Check every 30 seconds

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/api/environments')
def get_environments():
    """API endpoint to get environment data"""
    return jsonify(environment_data)

@app.route('/api/health')
def get_health_status():
    """API endpoint to get health status"""
    return jsonify(health_status)

@app.route('/api/health/check')
def trigger_health_check():
    """API endpoint to trigger immediate health check"""
    update_health_status()
    return jsonify({"status": "updated", "health": health_status})

# Initialize data when the app starts
def initialize_app():
    load_environment_data()
    # Start health check worker in background thread
    health_thread = threading.Thread(target=health_check_worker, daemon=True)
    health_thread.start()
    # Initial health check
    update_health_status()

# Initialize the app immediately
initialize_app()

# Remove redundant app.run - use 'flask run' or main.py instead
