# Vision - Environment Information Dashboard

## Overview

Vision is an internal web application designed for developers to provide a centralized source of truth for environment-related information. The application serves as a dashboard that displays product environments, their health status, database configurations, and other critical infrastructure details. The primary goal is to eliminate the need for developers to hunt through multiple systems to find environment-specific information.

The application is built with a focus on low maintenance, using a simple architecture with hardcoded YAML data sources that can be easily updated by development teams.

## Recent Updates (August 2025)

✓ **Enhanced Health Indicators**: Implemented vibrant neon colors (#00ff80 green, #ff1744 red, #ff9500 orange) with glow effects removed for cleaner appearance
✓ **MS SQL Server Migration**: Fully migrated from PostgreSQL/MySQL to MS SQL exclusively with dual-driver support (pyodbc + pymssql)
✓ **Poetry Package Management**: Migrated to Poetry for dependency management with comprehensive pyproject.toml
✓ **Single README**: Completely rewritten documentation with Poetry-based setup instructions
✓ **Poetry Scripts**: Added `poetry run start` command for easy application startup
✓ **Clean Architecture**: Removed redundant app.run calls, now properly configured with main() function entry point
✓ **Port Configuration**: Honors PORT variable from .env file, works with Poetry commands and direct Python execution
✓ **Development Tools**: Added dev dependencies (pytest, black, flake8) for code quality and testing

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- AngularJS (1.8.2) single-page application with a main controller pattern
- Bootstrap 5.3.0 for responsive UI components and styling
- Font Awesome 6.4.0 for iconography
- Real-time health status updates with visual indicators
- Accordion-based layout for organizing environment information

**Backend Architecture**
- Flask-based Python web server with minimal API endpoints
- RESTful API design with `/api/environments` and `/api/health` endpoints
- YAML-based data storage for environment configurations
- Background threading for health monitoring of environment URLs
- Periodic health checks using HTTP requests with timeout handling

**Data Management**
- YAML file (`data/environments.yaml`) serves as the single source of truth
- Nested data structure supporting multiple products, environments, and database configurations
- In-memory caching of environment data and health status
- Global variables for storing runtime state

**Health Monitoring System**
- Automated URL health checking with 5-second timeouts
- MS SQL Server database connectivity monitoring with dual-driver support (pyodbc + pymssql fallback)
- Background thread for continuous health status updates (30-second intervals)
- HTTP status code validation (200 = healthy) and MS SQL database query validation
- Real-time health indicator updates in both detailed and monitor views with enhanced vibrant colors
- Comprehensive health statistics including environments, microservices, and databases
- Enhanced visibility with bright neon colors (#00ff80 green, #ff1744 red, #ff9500 orange) and glow effects

**Error Handling and Logging**
- Comprehensive logging configuration with DEBUG level
- Try-catch blocks for YAML loading and HTTP requests
- Graceful degradation when environment data fails to load
- User-friendly error messages in the frontend

## External Dependencies

**Frontend Libraries**
- AngularJS 1.8.2 (via Google CDN)
- Bootstrap 5.3.0 (via CDN)
- Font Awesome 6.4.0 (via CloudFlare CDN)

**Python Libraries**
- Flask - Web framework for API endpoints and template rendering
- PyYAML - YAML file parsing and data loading
- Requests - HTTP client for health check functionality
- pyodbc - Primary MS SQL Server ODBC driver for database health monitoring
- pymssql - Fallback MS SQL Server driver for database connectivity
- Gunicorn - WSGI server for production deployment

**Deployment Tools**
- Docker & Docker Compose - Containerized deployment for company servers
- Nginx - Reverse proxy configuration for production
- Shell scripts - Automated deployment with `./deploy.sh` and `./deploy-simple.sh`

**Development Tools**
- Python logging module for application monitoring
- Flask's built-in development server with debug mode
- Environment variable support for configuration (SESSION_SECRET)

**Runtime Dependencies**
- No external databases required
- No authentication services (internal tool)
- No third-party APIs beyond health check URLs defined in YAML
- Static file serving through Flask for CSS/JS assets

**Deployment Architecture**
- **Company Servers**: Docker-based deployment with one-command setup
- **Replit Environment**: Direct Python execution with gunicorn
- **Production**: Nginx reverse proxy with SSL support and health monitoring