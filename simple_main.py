#!/usr/bin/env python3
"""
Simple startup script that bypasses the health check initialization
This will get the Flask server running immediately
"""
import os
import signal
import sys
from flask import Flask, render_template, jsonify

# Simple Flask app without health checks
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

# Configure Jinja2 to use different delimiters to avoid conflicts with AngularJS
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

# Simple in-memory data
environment_data = {
    "product_versions": [
        {
            "product_name": "Test Product",
            "environments": [
                {
                    "name": "Development",
                    "url": "https://dev.example.com",
                    "status": "healthy",
                    "microservices": [
                        {"name": "API", "server_url": "https://api.dev.example.com"},
                        {"name": "Auth", "server_url": "https://auth.dev.example.com"}
                    ],
                    "databases": []
                }
            ]
        }
    ]
}

health_status = {
    "env_https://dev.example.com": True,
    "ms_https://api.dev.example.com": True,
    "ms_https://auth.dev.example.com": False
}

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
    return jsonify({"status": "updated", "health": health_status})

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Stopping Vision Dashboard...')
    sys.exit(0)

def main():
    """Main entry point for the application"""
    signal.signal(signal.SIGINT, signal_handler)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Vision Dashboard on http://localhost:{port}")
    print("🌐 Web interface will be available immediately")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print('\n🛑 Vision Dashboard stopped')
    finally:
        print('🔄 Cleaning up...')
        os._exit(0)

if __name__ == '__main__':
    main()