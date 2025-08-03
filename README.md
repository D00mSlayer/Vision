# Vision - Environment Information Dashboard

Vision is an internal web application that provides a centralized dashboard for monitoring product environments, health status, database configurations, and microservices. Perfect for development teams and executive displays.

## 🚀 Quick Start

**One-Command Setup & Run:**

```bash
# Download, setup, and start everything
./start.sh

# Application will be available at http://localhost:5000
```

**Custom Port:**

There are three ways to set a custom port:

```bash
# Method 1: Set PORT environment variable before running
PORT=5099 ./start.sh

# Method 2: Export PORT and then run
export PORT=5099
./start.sh

# Method 3: Create a .env file (copy from .env.example)
cp .env.example .env
# Edit .env file to set PORT=5099
./start.sh

# Application will be available at http://localhost:5099
```

**What the script does:**
- ✅ Checks Python 3.8+ and pip3
- ✅ Verifies system dependencies for MS SQL drivers
- ✅ Creates clean virtual environment
- ✅ Installs all Python packages
- ✅ Creates necessary directories
- ✅ Starts the application

## 🔧 Live Configuration Updates

Edit `data/environments.yaml` and refresh your browser to see changes immediately.
No restart needed!

## 📋 What You Get

- **Real-time Health Monitoring**: Automatic health checks for URLs and MS SQL databases
- **Dual Display Modes**: Detailed view for developers + Monitor view for floor displays
- **Live Configuration**: Edit `data/environments.yaml` and refresh browser to see changes
- **Executive Dashboard**: High-level statistics and visual health indicators
- **Auto-scrolling**: Perfect for large displays showing 20+ microservices

## ⚙️ Configuration

### Port Configuration

The application uses the `PORT` environment variable throughout:

```bash
# Set custom port for any deployment method
export PORT=5099

# For any method
export PORT=5099
./run.sh
```

**Default port:** 5000 (use PORT environment variable to change)

### Environment Data

Edit `data/environments.yaml` to add your environments:

```yaml
product_versions:
  - name: "Your Product v1.0"
    environments:
      - name: "Development"
        url: "https://dev.yourcompany.com"
        git_branch: "develop"
        databases:
          - type: "primary"
            host: "sql-dev.yourcompany.com"
            port: 1433
            database_name: "yourapp_dev"
            username: "dev_user"
            password: "dev_password"
        microservices:
          - name_of_service: "AuthService"
            server_url: "https://auth-dev.yourcompany.com"
            port: 8080
            git_branch: "develop"
```

After editing, just refresh your browser - changes appear immediately!

## 🖥 Using the Dashboard

### Detailed View (Default)
- Expandable sections for each environment
- Complete database and microservice information
- Perfect for developers and detailed monitoring

### Monitor View
- Click "Switch to Monitor View" button
- Auto-scrolling for environments with many services
- Large, visible health indicators
- Perfect for floor displays and executive dashboards

### Health Status Colors
- 🟢 **Green**: Service is healthy and responding
- 🔴 **Red**: Service is offline or unreachable  
- 🟠 **Orange**: Service is being checked

## 🐛 Troubleshooting

### Port Already in Use
The script automatically checks if ports are available and provides helpful solutions:

```bash
# The script will detect port conflicts and suggest solutions:
# ❌ Error: Port 5000 is already in use!
# 
# Solutions:
# 1. Use a different port: PORT=5099 ./start.sh
# 2. Kill the process using port 5000
# 3. Edit .env file to use a different port

# Use any of these approaches:
PORT=5099 ./start.sh
# or edit .env file to set PORT=5099
```

### Prerequisites (Linux)

The script will check and guide you to install:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv build-essential unixodbc-dev freetds-dev
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip
sudo yum groupinstall 'Development Tools'
sudo yum install unixODBC-devel freetds-devel
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
sudo dnf groupinstall 'Development Tools'
sudo dnf install unixODBC-devel freetds-devel
```

### Missing Dependencies
```bash
# Re-run the complete setup
./start.sh
```

### Virtual Environment Issues
```bash
# The script automatically recreates the virtual environment
./start.sh
```

### Script Permission Issues
```bash
# Fix script permissions
chmod +x start.sh
./start.sh
```

### Configuration Not Updating
Changes to `data/environments.yaml` appear immediately - just refresh your browser

### Database Connection Issues
- The app uses dual drivers (pyodbc + pymssql) for MS SQL
- If one fails, it automatically tries the other
- Check your database credentials in `data/environments.yaml`

## 💡 Tips

- Changes to `data/environments.yaml` appear immediately with browser refresh
- Use Monitor View for impressive floor displays
- Health checks run automatically every 30 seconds
- Green = healthy, Red = offline, Orange = checking

---

**That's it! Vision Dashboard is ready to impress your team and management with real-time infrastructure monitoring.**

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