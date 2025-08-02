# Vision - Environment Information Dashboard

Vision is an internal web application that provides a centralized dashboard for monitoring product environments, health status, database configurations, and microservices. Perfect for development teams and executive displays.

## 🚀 Quick Start - Choose Your Method

### Method 1: Docker (Recommended for Company Servers)
```bash
# 1. Clone the project
git clone <your-repo-url>
cd vision-dashboard

# 2. Run with custom port (easy way)
PORT=5099 ./run-docker.sh

# OR manually:
export PORT=5099
docker compose up -d

# Application will be available at http://localhost:5099
```

### Method 2: Direct Python (Simple Setup)
```bash
# 1. Clone the project
git clone <your-repo-url>
cd vision-dashboard

# 2. Install dependencies
pip3 install --user flask pyyaml requests pyodbc pymssql gunicorn

# 3. Set custom port (optional)
export PORT=5099

# 4. Set session secret
export SESSION_SECRET="your-secure-32-character-key"

# 5. Run the application
gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app
```

## 🔧 Live Configuration Updates

Your `data/environments.yaml` file is mounted for live updates:

**Docker Setup**: Changes to `data/environments.yaml` reflect immediately with browser refresh
**Direct Python**: Changes reflect immediately with browser refresh

No restart needed - just refresh your browser!

## 📋 What You Get

- **Real-time Health Monitoring**: Automatic health checks for URLs and MS SQL databases
- **Dual Display Modes**: Detailed view for developers + Monitor view for floor displays
- **Live Configuration**: Edit `data/environments.yaml` and refresh browser to see changes
- **Executive Dashboard**: High-level statistics and visual health indicators
- **Auto-scrolling**: Perfect for large displays showing 20+ microservices

## ⚙️ Configuration

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
docker compose up -d
# OR
gunicorn --bind 0.0.0.0:5099 --workers 1 main:app
```

### Missing Dependencies
```bash
pip3 install --user flask pyyaml requests pyodbc pymssql gunicorn
```

### Docker App Not Loading
If your Docker container is running but app won't load:

**Step 1: Debug the issue**
```bash
./debug-docker.sh
```

**Step 2: Fix the common issues**
```bash
# Stop the current container
docker compose down

# Make sure PORT is set and restart
PORT=5099 docker compose up -d

# Check if it's working
curl http://localhost:5099/api/health
```

**Step 3: If still not working, try rebuild**
```bash
docker compose down
docker compose build --no-cache
PORT=5099 docker compose up -d
```

### Configuration Not Updating
- For Docker: Changes to `data/environments.yaml` are mounted and appear immediately
- For Direct Python: Changes appear immediately  
- Just refresh your browser after editing the file

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