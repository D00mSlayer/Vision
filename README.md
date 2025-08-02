# Vision - Environment Information Dashboard

Vision is an internal web application that provides a centralized dashboard for monitoring product environments, health status, database configurations, and microservices. Perfect for development teams and executive displays.

## 🚀 Quick Start

**Super Simple Setup:**

```bash
# 1. Setup (creates virtual environment and installs everything)
./setup.sh

# 2. Run the application
./run.sh

# Application will be available at http://localhost:5000
```

**Manual Setup:**

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install flask pyyaml requests pymssql gunicorn

# 3. Start the application
python main.py
```

**Custom Port:**

```bash
# Set custom port for any method
export PORT=5099
./run.sh

# Application will be available at http://localhost:5099
```

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
```bash
# Use a different port
export PORT=5099
./run.sh
```

### Missing Dependencies
```bash
# Run setup again
./setup.sh
```

### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
./setup.sh
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