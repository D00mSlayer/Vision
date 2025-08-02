"""
Vision App Routes Module
Handles all web routes for dashboard and monitor views
"""

from flask import render_template, jsonify
from app import app
from services.environment_service import EnvironmentService
from services.health_service import HealthService


# Initialize services
env_service = EnvironmentService()
health_service = HealthService()


@app.route('/')
def dashboard():
    """Render the detailed dashboard view"""
    return render_template('dashboard.html')


@app.route('/monitor')
def monitor():
    """Render the full-screen monitor view"""
    return render_template('monitor.html')


@app.route('/api/environments')
def get_environments():
    """API endpoint to get environment data"""
    try:
        data = env_service.get_environment_data()
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error loading environment data: {e}")
        return jsonify({'error': 'Failed to load environment data'}), 500


@app.route('/api/health')
def get_health():
    """API endpoint to get health status"""
    try:
        health_status = health_service.get_health_status()
        return jsonify(health_status)
    except Exception as e:
        app.logger.error(f"Error getting health status: {e}")
        return jsonify({'error': 'Failed to get health status'}), 500


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('dashboard.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {e}")
    return render_template('dashboard.html'), 500