# Vision Dashboard - Quick Start Guide

Get Vision Dashboard running in your company in less than 5 minutes!

## 🚀 Super Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd vision-dashboard

# 2. Run the one-command deployment
./deploy.sh
```

**That's it!** The application will be running at http://localhost:5000

## 📝 What the deployment script does:

1. ✅ Checks if Docker is installed
2. ✅ Creates secure configuration files
3. ✅ Generates a unique session key
4. ✅ Builds the Docker container
5. ✅ Starts the application
6. ✅ Verifies everything is working

## 🔧 Quick Configuration

### Update your environments
Edit `data/environments.yaml` with your company's actual environments:

```yaml
product_versions:
  - name: "YourProduct v1.0"
    environments:
      - name: "Development"
        url: "https://dev.yourcompany.com"
        databases:
          - host: "sql-dev.yourcompany.com"
            port: 1433
            database_name: "yourapp_dev"
            username: "your_user"
            password: "your_password"
        microservices:
          - name_of_service: "AuthService"
            server_url: "https://auth-dev.yourcompany.com"
```

### Restart to apply changes
```bash
docker-compose restart
```

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

## 📊 Health Monitoring

The application automatically monitors:
- **Environment URLs**: Main application health
- **Microservice URLs**: Individual service status
- **MS SQL Databases**: Connection and query validation

Updates every 30 seconds automatically.

## 🛠 Common Commands

```bash
# View logs
docker-compose logs -f

# Stop the application  
docker-compose down

# Restart the application
docker-compose restart

# Update the application
git pull && docker-compose build && docker-compose up -d

# Check application status
curl http://localhost:5000/api/health
```

## 🔒 Security Notes

- The deployment script generates a secure session key automatically
- Update `data/environments.yaml` with your real database credentials
- For production, consider using environment variables for sensitive data

## 📞 Need Help?

1. Check the full [README.md](README.md) for detailed documentation
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options
3. View application logs: `docker-compose logs -f`
4. Contact your development team

## 🎯 Next Steps

1. **Customize your data**: Update `data/environments.yaml` with real environments
2. **Set up monitoring**: Configure for your floor displays
3. **Production deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
4. **Team training**: Show your team the monitor view for impressive displays

---

**Vision Dashboard - Making infrastructure monitoring simple and impressive!**