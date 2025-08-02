"""
Vision App - Main Application Module
Infrastructure monitoring and health check application
"""

import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

# Configure Jinja2 to use different delimiters to avoid conflicts with AngularJS
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

# Import routes after app creation to avoid circular imports
import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)