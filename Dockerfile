# Vision Dashboard Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for MS SQL Server connectivity
RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure FreeTDS for MS SQL Server
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver for Linux & MSSQL\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so\n\
FileUsage = 1\n\
UsageCount = 1" > /etc/odbcinst.ini

# Copy requirements first for better caching
COPY requirements_docker.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV SESSION_SECRET=default-change-in-production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--keep-alive", "5", "main:app"]