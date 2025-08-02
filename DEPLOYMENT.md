# Vision Dashboard - Company Deployment Guide

This guide provides step-by-step instructions for deploying Vision Dashboard in your company environment.

## 🚀 Quick Deployment (Recommended)

### Option 1: One-Command Deployment (Company Servers with Docker)

```bash
# Clone the repository
git clone <your-repo-url>
cd vision-dashboard

# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

The script will automatically:
- Check Docker installation
- Create configuration files
- Generate secure session keys  
- Build and start the application
- Verify deployment success

**Requirements**: Docker and Docker Compose installed on the server

### Option 2: Manual Docker Compose (Company Servers)

```bash
# Clone and setup
git clone <your-repo-url>
cd vision-dashboard

# Create environment file
cp .env.example .env
# Edit .env with your secure session key

# Start the application
docker-compose up -d

# Application will be available at http://localhost:5000
```

### Option 3: Direct Python Deployment (Replit/Simple Servers)

```bash
# Clone the repository
git clone <your-repo-url>
cd vision-dashboard

# Install dependencies
pip install flask pyyaml requests pyodbc pymssql gunicorn

# Create environment file
cp .env.example .env
# Edit .env with your secure session key

# Run the application
export SESSION_SECRET="your-secure-secret-key"
gunicorn --bind 0.0.0.0:5000 --workers 2 main:app

# Application will be available at http://localhost:5000
```

## 📋 Server Requirements

### Minimum Requirements
- **CPU**: 1 core
- **RAM**: 512MB
- **Storage**: 1GB
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Software**: Docker & Docker Compose

### Recommended for Production
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 5GB
- **Network**: Internal company network access
- **Monitoring**: Log aggregation (Splunk, ELK, etc.)

## 🔧 Configuration

### 1. Environment Data Setup

Edit `data/environments.yaml` with your company's environments:

```yaml
product_versions:
  - name: "YourProduct v1.0"
    environments:
      - name: "Development"
        url: "https://dev.yourcompany.com"
        git_branch: "develop"
        git_tag: "v1.0.0-dev"
        databases:
          - type: "primary"
            host: "sql-dev.yourcompany.com"
            port: 1433
            database_name: "yourapp_dev"
            username: "dev_user"
            password: "secure_password"
        microservices:
          - name_of_service: "AuthService"
            server_url: "https://auth-dev.yourcompany.com"
            port: 8080
            git_branch: "develop"
            git_tag: "auth-v1.0"
```

### 2. Security Configuration

Update `.env` file:

```bash
# Generate secure session key (32+ characters)
SESSION_SECRET=$(openssl rand -hex 32)

# Production settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### 3. Network Configuration

#### Internal Network Only
Default configuration works for internal company networks.

#### External Access with Authentication
For external access, add authentication:

```python
# Add to app.py
from flask_login import LoginManager, login_required

@app.route('/')
@login_required
def index():
    # existing code
```

## 🏗 Production Deployment Options

### Option 1: Simple Docker Deployment

Best for: Small teams, internal tools, quick setup

```bash
# Production docker-compose.yml
version: '3.8'
services:
  vision-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SESSION_SECRET=${SESSION_SECRET}
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs
    restart: unless-stopped
```

### Option 2: Nginx Reverse Proxy

Best for: Multiple applications, SSL termination, load balancing

```bash
# Enable nginx in docker-compose.yml
# Uncomment the nginx service section

# Configure your domain
sed -i 's/vision.yourcompany.com/your-actual-domain.com/' nginx.conf

# Start with nginx
docker-compose up -d
```

### Option 3: Kubernetes Deployment

Best for: Large organizations, container orchestration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vision-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vision-dashboard
  template:
    metadata:
      labels:
        app: vision-dashboard
    spec:
      containers:
      - name: vision-dashboard
        image: vision-dashboard:latest
        ports:
        - containerPort: 5000
        env:
        - name: SESSION_SECRET
          valueFrom:
            secretKeyRef:
              name: vision-secrets
              key: session-secret
```

## 🔍 Monitoring & Maintenance

### Health Monitoring

The application includes built-in health checks:

```bash
# Check application health
curl http://localhost:5000/api/health

# Check with Docker
docker-compose ps
docker-compose logs vision-app
```

### Log Management

```bash
# View real-time logs
docker-compose logs -f vision-app

# Rotate logs (setup logrotate)
/etc/logrotate.d/vision-dashboard:
/opt/vision-dashboard/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 vision vision
}
```

### Performance Monitoring

Monitor key metrics:
- **Response Time**: Health check endpoint latency
- **Memory Usage**: Container memory consumption
- **Database Connections**: MS SQL connection pool
- **Health Check Success Rate**: Environment availability

### Backup Strategy

```bash
# Backup configuration
tar -czf vision-backup-$(date +%Y%m%d).tar.gz \
    data/ .env docker-compose.yml

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backups/vision-$DATE.tar.gz /opt/vision-dashboard/data
find /backups -name "vision-*.tar.gz" -mtime +30 -delete
```

## 🔒 Security Best Practices

### Network Security
- Deploy behind company firewall
- Use VPN for external access
- Restrict database access to application servers only

### Application Security
- Regular dependency updates
- Strong session secrets (32+ characters)
- Environment variable security
- Log sensitive data filtering

### Access Control
```bash
# Create dedicated user
useradd -r -s /bin/false vision
chown -R vision:vision /opt/vision-dashboard

# File permissions
chmod 600 .env
chmod 644 data/environments.yaml
chmod 755 deploy.sh
```

## 📊 Scaling Considerations

### Vertical Scaling
- Increase container resources
- Optimize health check intervals
- Add database connection pooling

### Horizontal Scaling
```yaml
# docker-compose.yml for load balancing
version: '3.8'
services:
  vision-app:
    build: .
    deploy:
      replicas: 3
    environment:
      - SESSION_SECRET=${SESSION_SECRET}
      
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - vision-app
```

### Database Optimization
- Connection pooling for MS SQL
- Query optimization for health checks
- Caching for environment data

## 🐛 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker-compose logs vision-app

# Verify environment file
cat .env | grep SESSION_SECRET
```

#### 2. Database Connection Issues
```bash
# Test MS SQL connectivity
docker run --rm -it --network host \
  mcr.microsoft.com/mssql-tools \
  sqlcmd -S your-server -U username -P password

# Check application database logs
docker-compose logs vision-app | grep "database health check"
```

#### 3. Health Checks Failing
```bash
# Test URL connectivity from container
docker-compose exec vision-app curl -I https://your-environment.com

# Check DNS resolution
docker-compose exec vision-app nslookup your-environment.com

# Verify SSL certificates
docker-compose exec vision-app openssl s_client -connect your-environment.com:443
```

#### 4. Performance Issues
```bash
# Monitor container resources
docker stats vision-dashboard

# Check health check intervals
docker-compose logs vision-app | grep "Health status updated"

# Optimize health check frequency
# Edit app.py: time.sleep(60)  # Increase from 30 to 60 seconds
```

## 🔄 Updates & Maintenance

### Regular Updates
```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Update dependencies
docker-compose build --no-cache
```

### Automated Updates
```bash
#!/bin/bash
# /opt/scripts/update-vision.sh

cd /opt/vision-dashboard
git pull origin main

if git diff-tree --name-only HEAD HEAD~1 | grep -E "(requirements.txt|Dockerfile)" > /dev/null; then
    echo "Dependencies changed, rebuilding..."
    docker-compose build --no-cache
fi

docker-compose up -d
docker-compose logs --tail=20 vision-app
```

### Configuration Changes
```bash
# Update environment data
vim data/environments.yaml

# Restart to reload configuration
docker-compose restart vision-app

# Verify changes
curl http://localhost:5000/api/environments
```

## 📞 Support & Documentation

### Internal Documentation
- Keep this deployment guide updated
- Document environment-specific configurations
- Maintain troubleshooting runbook

### Monitoring Integration
```bash
# Integrate with company monitoring
# Prometheus metrics endpoint
curl http://localhost:5000/metrics

# Splunk log forwarding
# Configure docker logging driver in docker-compose.yml
```

### Team Training
- Application overview and features
- Monitor view for floor displays
- Health indicator meanings
- Basic troubleshooting

---

**This deployment guide ensures your team can easily deploy and maintain Vision Dashboard in your company environment.**