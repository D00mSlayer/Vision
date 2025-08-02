import os
import yaml
import logging
import requests
from flask import Flask, render_template, jsonify
from urllib.parse import urlparse
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

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

def update_health_status():
    """Update health status for all URLs"""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
