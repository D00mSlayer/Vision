import os
import yaml
import logging
import requests
import pyodbc
import pymssql
from flask import Flask, render_template, jsonify, request
from urllib.parse import urlparse, urlunparse
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
app.secret_key = os.environ.get("SESSION_SECRET",
                                "dev_secret_key_change_in_production")

# Configure Jinja2 to use different delimiters to avoid conflicts with AngularJS
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

# Global variable to store health status only
health_status = {}


def load_environment_data():
    """Load environment data from YAML file - fresh every time"""
    try:
        with open('data/environments.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        app.logger.error(f"Error loading environment data: {e}")
        return {"product_versions": []}


def load_bookmarks_data():
    """Load bookmarks data from YAML file - fresh every time"""
    try:
        with open('data/bookmarks.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        app.logger.error(f"Error loading bookmarks data: {e}")
        return {"bookmarks": []}


def fuzzy_search_bookmarks(query, bookmarks):
    """Perform fuzzy search on bookmarks with typo tolerance"""
    if not query:
        return bookmarks

    import re
    from difflib import SequenceMatcher

    query = query.lower().strip()
    results = []

    def similarity_score(a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def contains_fuzzy(text, search_term):
        """Check if text contains search term with fuzzy matching"""
        text = text.lower()
        # Direct substring match gets highest score
        if search_term in text:
            return 1.0

        # Check for partial word matches
        words = text.split()
        best_score = 0
        for word in words:
            score = similarity_score(word, search_term)
            if score > best_score:
                best_score = score

        return best_score

    for bookmark in bookmarks:
        max_score = 0

        # Search in name
        name_score = contains_fuzzy(bookmark.get('name', ''), query)
        max_score = max(max_score, name_score)

        # Search in description
        desc_score = contains_fuzzy(bookmark.get('description', ''), query)
        max_score = max(max_score, desc_score)

        # Search in main URL
        url_score = contains_fuzzy(bookmark.get('main_url', ''), query)
        max_score = max(max_score, url_score)

        # Search in git link
        git_score = contains_fuzzy(bookmark.get('git_link', ''), query)
        max_score = max(max_score, git_score)

        # Search in sub URLs
        for sub_url in bookmark.get('sub_urls', []):
            sub_name_score = contains_fuzzy(sub_url.get('name', ''), query)
            sub_url_score = contains_fuzzy(sub_url.get('url', ''), query)
            max_score = max(max_score, sub_name_score, sub_url_score)

        # Include if similarity is above threshold (0.4 for typo tolerance)
        if max_score >= 0.4:
            results.append({'bookmark': bookmark, 'score': max_score})

    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    return [result['bookmark'] for result in results]


def check_url_health(url):
    """Check if a URL is reachable with faster timeout"""
    try:
        response = requests.get(url, timeout=2)  # Reduced from 5 to 2 seconds
        return response.status_code == 200
    except:
        return False


def check_database_health(host, port, database_name, username, password):
    """Check if a MS SQL database is accessible using pymssql (FreeTDS) with faster timeouts"""

    # Since ODBC drivers are not properly configured in this environment,
    # fall back to pymssql which uses FreeTDS directly
    try:
        connection = pymssql.connect(
            server=host,
            user=username,
            password=password,
            database=database_name,
            port=str(port),
            timeout=2,  # Reduced from 5 to 2 seconds
            login_timeout=2,  # Reduced from 5 to 2 seconds
            # Add encryption support for pymssql
            charset='UTF-8')
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return True

    except Exception as e:
        app.logger.debug(
            f"MS SQL database health check failed for {host}:{port}/{database_name}: {e}"
        )
        return False


def update_health_status():
    """Update health status for all URLs and databases"""
    global health_status

    environment_data = load_environment_data()

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
                ms_port = microservice.get('port')
                if ms_url and ms_port:
                    # Parse the URL and add the port for health checking
                    parsed_url = urlparse(ms_url)
                    # Create URL with port for health checking
                    health_check_url = f"{parsed_url.scheme}://{parsed_url.hostname}:{ms_port}{parsed_url.path}"
                    health_key = f"ms_{ms_url}"
                    health_status[health_key] = check_url_health(health_check_url)

            for database in env.get('databases', []):
                if all(
                        key in database for key in
                    ['host', 'port', 'database_name', 'username', 'password']):
                    db_identifier = f"{database['host']}:{database['port']}/{database['database_name']}"
                    health_key = f"db_{db_identifier}"
                    health_status[health_key] = check_database_health(
                        database['host'], database['port'],
                        database['database_name'], database['username'],
                        database['password'])


def health_check_worker():
    """Background worker to continuously update health status"""
    while True:
        try:
            update_health_status()
        except Exception as e:
            app.logger.error(f"Health check error: {e}")
        time.sleep(15)  # Check every 15 seconds (reduced from 30)


@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')


@app.route('/api/environments')
def get_environments():
    """API endpoint to get environment data - always fresh"""
    environment_data = load_environment_data()
    return jsonify(environment_data)


@app.route('/api/bookmarks')
def get_bookmarks():
    """API endpoint to get all bookmarks"""
    bookmarks_data = load_bookmarks_data()
    return jsonify(bookmarks_data)


@app.route('/api/bookmarks/search')
def search_bookmarks():
    """API endpoint to search bookmarks with fuzzy matching"""
    query = request.args.get('q', '')
    bookmarks_data = load_bookmarks_data()

    if query:
        filtered_bookmarks = fuzzy_search_bookmarks(
            query, bookmarks_data.get('bookmarks', []))
        return jsonify({'bookmarks': filtered_bookmarks, 'query': query})
    else:
        return jsonify(bookmarks_data)


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
    # Start health check worker in background thread
    health_thread = threading.Thread(target=health_check_worker, daemon=True)
    health_thread.start()
    app.logger.info("Background health monitoring started")


# Initialize app with threading to prevent blocking
def delayed_health_check():
    """Start initial health check after Flask server is running"""
    import time
    time.sleep(5)  # Wait 5 seconds for server to fully start
    app.logger.info("Starting initial health check...")
    update_health_status()


# Initialize the app immediately but defer health checks
initialize_app()

# Start delayed health check in background
delayed_health_thread = threading.Thread(target=delayed_health_check,
                                         daemon=True)
delayed_health_thread.start()

# Remove redundant app.run - use 'flask run' or main.py instead
