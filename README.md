# Vision - Environment Information Dashboard

Vision is an internal web application designed for developers to provide a centralized source of truth for environment-related information. The application serves as a dashboard that displays product environments, their health status, database configurations, and other critical infrastructure details.

## 🚀 Quick Start with Docker

The easiest way to run Vision is using Docker Compose:

```bash
# Clone and navigate to the project
git clone <your-repo-url>
cd vision-dashboard

# Start the application
docker compose up -d

# The application will be available at http://localhost:5000
```

That's it! The application will automatically:
- Install all dependencies
- Start the Flask server
- Begin health monitoring
- Serve the web interface

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Usage](#usage)
- [Health Monitoring](#health-monitoring)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🎯 Core Features
- **Centralized Environment Information**: Single source of truth for all product environments
- **Real-time Health Monitoring**: Automatic health checks for URLs, microservices, and MS SQL databases
- **Dual Display Modes**: 
  - Detailed interactive view for developers
  - Monitor-friendly display with auto-scrolling for floor displays
- **MS SQL Server Support**: Native connectivity with dual-driver support (pyodbc + pymssql)
- **Executive Dashboard**: High-level statistics and visual health indicators

### 🎨 Visual Features
- **Enhanced Health Indicators**: Vibrant, distinguishable colors for easy status identification
- **Responsive Design**: Works on desktop, tablet, and large monitors
- **Auto-scrolling Interface**: Perfect for large displays showing 20+ microservices
- **Real-time Updates**: Health status updates every 30 seconds

## 🏗 Architecture

### Frontend
- **AngularJS 1.8.2**: Single-page application with main controller pattern
- **Bootstrap 5.3.0**: Responsive UI components and styling
- **Font Awesome 6.4.0**: Comprehensive iconography

### Backend
- **Flask**: Python web framework with RESTful API design
- **Real-time Health Monitoring**: Background threading with 30-second intervals
- **YAML Configuration**: File-based environment data management

### Database Support
- **MS SQL Server**: Primary database platform
- **Dual Driver Support**: 
  - pyodbc with ODBC Driver 18 (preferred)
  - pymssql as fallback
- **Connection Pooling**: Optimized database connectivity

### Health Monitoring
- **URL Health Checks**: HTTP status validation with 5-second timeouts
- **Database Connectivity**: MS SQL connection testing with query validation
- **Microservice Monitoring**: Real-time status tracking
- **Visual Indicators**: Bright neon colors (#00ff80 green, #ff1744 red, #ff9500 orange)

## 🔧 Installation Methods

### Method 1: Docker Compose (Recommended)

1. **Prerequisites**: Docker and Docker Compose installed

2. **Quick Start**:
   ```bash
   docker compose up -d
   ```

3. **Access**: Open http://localhost:5000

### Method 2: Local Development

1. **Prerequisites**:
   - Python 3.11+
   - MS SQL Server ODBC drivers (optional, pymssql used as fallback)

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   ```bash
   export SESSION_SECRET="your-secure-secret-key"
   ```

4. **Run Application**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

### Method 3: Production Deployment

1. **System Requirements**:
   - Linux server (Ubuntu/CentOS/RHEL)
   - Python 3.11+
   - Nginx (recommended for reverse proxy)
   - MS SQL Server ODBC drivers

2. **Production Setup**:
   ```bash
   # Install system dependencies
   apt-get update
   apt-get install -y python3.11 python3-pip nginx

   # Install Python dependencies
   pip install -r requirements.txt

   # Configure systemd service (see deployment section)
   systemctl enable vision-dashboard
   systemctl start vision-dashboard
   ```

## ⚙️ Configuration

### Environment Data

Edit `data/environments.yaml` to configure your environments:

```yaml
product_versions:
  - name: "Your Product v1.0"
    environments:
      - name: "Development"
        url: "https://dev.yourcompany.com"
        git_branch: "develop"
        git_tag: "v1.0.0-dev"
        databases:
          - type: "primary"
            host: "sqlserver.dev.yourcompany.com"
            port: 1433
            database_name: "yourapp_dev"
            username: "dev_user"
            password: "dev_password"
        microservices:
          - name_of_service: "AuthService"
            server_url: "https://auth.dev.yourcompany.com"
            port: 8080
            git_branch: "develop"
            git_tag: "auth-v1.0"
```

### Environment Variables

```bash
# Required
SESSION_SECRET="your-secure-secret-key-min-32-chars"

# Optional - for custom configuration
FLASK_ENV="production"
FLASK_DEBUG="false"
```

### Health Check Configuration

The application automatically monitors:
- **Environment URLs**: Main application endpoints
- **Microservice URLs**: Individual service health endpoints
- **MS SQL Databases**: Connection and query validation

Update intervals:
- **Health Checks**: Every 30 seconds
- **UI Updates**: Real-time via JavaScript polling

## 🖥 Usage

### Detailed View
- Expandable sections for each environment
- Complete database and microservice information
- Git branch and tag details
- Splunk configuration display

### Monitor View
- Toggle with "Switch to Monitor View" button
- Auto-scrolling for environments with 20+ microservices
- Large, easily readable health indicators
- Executive-level statistics dashboard

### Health Status Colors
- **🟢 Green (#00ff80)**: Service is healthy and responding
- **🔴 Red (#ff1744)**: Service is offline or unreachable
- **🟠 Orange (#ff9500)**: Service is being checked or in transition

## 🏥 Health Monitoring

### How It Works

1. **Background Threading**: Health checks run continuously in separate threads
2. **Database Connectivity**: 
   - Attempts connection with configured credentials
   - Executes `SELECT 1` query to verify functionality
   - Supports both pyodbc and pymssql drivers
3. **URL Monitoring**: 
   - HTTP GET requests with 5-second timeout
   - Validates 200 status code responses
4. **Real-time Updates**: Status changes are immediately reflected in UI

### Troubleshooting Health Checks

#### Database Connection Issues
```bash
# Check database connectivity manually
python -c "
import pymssql
conn = pymssql.connect(
    server='your-server', 
    user='username', 
    password='password', 
    database='database_name',
    port=1433
)
print('Connection successful')
conn.close()
"
```

#### URL Monitoring Issues
```bash
# Test URL accessibility
curl -I -m 5 https://your-environment-url.com
```

## 🔧 Development

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone <repo-url>
   cd vision-dashboard
   ```

2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Development Server**:
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=true
   python main.py
   ```

### Project Structure
```
vision-dashboard/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── data/
│   └── environments.yaml # Environment configuration
├── static/
│   ├── css/
│   │   └── styles.css    # Custom styling
│   └── js/
│       └── app.js        # AngularJS application
├── templates/
│   └── index.html        # Main template
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Environments

1. Edit `data/environments.yaml`
2. Add environment configuration following existing pattern
3. Application automatically reloads configuration
4. Health monitoring begins immediately

### Customizing Health Checks

Modify `app.py` functions:
- `check_url_health()`: URL monitoring logic
- `check_database_health()`: Database connectivity logic
- `update_health_status()`: Health check orchestration

## 🐛 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify dependencies
pip list

# Check logs
docker compose logs vision-app
```

#### 2. Database Connection Failures
```bash
# Verify MS SQL Server accessibility
telnet your-db-server 1433

# Check ODBC drivers
odbcinst -q -d

# Test pymssql connectivity
python -c "import pymssql; print('pymssql available')"
```

#### 3. Health Checks Not Working
```bash
# Check network connectivity
ping your-environment-url.com

# Verify SSL certificates
openssl s_client -connect your-environment-url.com:443

# Check application logs
tail -f /var/log/vision-dashboard/app.log
```

#### 4. UI Not Loading
```bash
# Check static file serving
curl http://localhost:5000/static/css/styles.css

# Verify AngularJS loading
curl http://localhost:5000/static/js/app.js

# Check browser console for JavaScript errors
```

### Performance Optimization

#### For Large Environments (50+ services)
1. **Increase Health Check Intervals**:
   ```python
   # In app.py, modify:
   time.sleep(60)  # Change from 30 to 60 seconds
   ```

2. **Optimize Database Connections**:
   ```python
   # Use connection pooling
   connection_pool = ConnectionPool(...)
   ```

3. **Enable Caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app)
   ```

### Monitoring and Logging

#### Application Logs
```bash
# View real-time logs
docker compose logs -f vision-app

# Application-specific logs
tail -f logs/vision-dashboard.log
```

#### Health Check Logs
```bash
# Database connection logs
grep "database health check" logs/vision-dashboard.log

# URL monitoring logs
grep "HTTP" logs/vision-dashboard.log
```

## 📦 Production Deployment

### Docker Production Setup

1. **Production Docker Compose**:
   ```yaml
   version: '3.8'
   services:
     vision-app:
       build: .
       ports:
         - "5000:5000"
       environment:
         - SESSION_SECRET=${SESSION_SECRET}
         - FLASK_ENV=production
       restart: unless-stopped
       volumes:
         - ./data:/app/data:ro
         - ./logs:/app/logs
   ```

2. **Nginx Reverse Proxy**:
   ```nginx
   server {
       listen 80;
       server_name vision.yourcompany.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Systemd Service

```ini
[Unit]
Description=Vision Dashboard
After=network.target

[Service]
Type=notify
User=vision
Group=vision
WorkingDirectory=/opt/vision-dashboard
Environment=SESSION_SECRET=your-secret-key
ExecStart=/opt/vision-dashboard/venv/bin/gunicorn --bind 0.0.0.0:5000 main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔒 Security Considerations

### Authentication
- Currently designed for internal networks
- Consider adding authentication for external access
- Use strong SESSION_SECRET values

### Network Security
- Deploy behind firewall for internal use
- Use HTTPS in production with SSL certificates
- Restrict database access to application servers

### Data Security
- Encrypt database passwords in configuration
- Use environment variables for sensitive data
- Regular security updates for dependencies

## 📈 Scaling

### Horizontal Scaling
- Multiple application instances behind load balancer
- Shared configuration via network storage
- Database connection pooling

### Vertical Scaling
- Increase health check worker threads
- Optimize database query performance
- Enable application caching

## 🤝 Contributing

1. **Development Workflow**:
   ```bash
   git checkout -b feature/your-feature
   # Make changes
   git commit -m "Add your feature"
   git push origin feature/your-feature
   # Create pull request
   ```

2. **Code Style**:
   - Follow PEP 8 for Python
   - Use meaningful variable names
   - Add comments for complex logic

3. **Testing**:
   ```bash
   # Run health checks manually
   python -c "from app import update_health_status; update_health_status()"
   
   # Test database connectivity
   python -c "from app import check_database_health; print(check_database_health('server', 1433, 'db', 'user', 'pass'))"
   ```

## 📞 Support

For issues and questions:
1. Check this README for common solutions
2. Review application logs for error details
3. Contact the development team
4. Create an issue in the project repository

---

**Built with ❤️ for monitoring infrastructure health and keeping teams informed.**