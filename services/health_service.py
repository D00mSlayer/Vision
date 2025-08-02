"""
Health Service Module
Handles health monitoring for environments, microservices, and databases
"""

import threading
import time
import requests
import logging
from services.environment_service import EnvironmentService

# Import database drivers with fallback handling
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False


class HealthService:
    """Service for monitoring system health"""
    
    def __init__(self):
        self.env_service = EnvironmentService()
        self.health_status = {}
        self.logger = logging.getLogger(__name__)
        self._monitoring_thread = None
        self._stop_monitoring = False
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._stop_monitoring = False
            self._monitoring_thread = threading.Thread(target=self._monitor_health, daemon=True)
            self._monitoring_thread.start()
            self.logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
    
    def _monitor_health(self):
        """Background thread for continuous health monitoring"""
        while not self._stop_monitoring:
            try:
                self._check_all_health()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_all_health(self):
        """Check health of all services"""
        environment_data = self.env_service.get_environment_data()
        if not environment_data:
            return
        
        for product in environment_data.get('product_versions', []):
            for env in product.get('environments', []):
                # Check environment URL
                env_key = f"env_{env['url']}"
                self.health_status[env_key] = self._check_url_health(env['url'])
                
                # Check microservices
                for service in env.get('microservices', []):
                    service_key = f"ms_{service['server_url']}"
                    self.health_status[service_key] = self._check_url_health(service['server_url'])
                
                # Check databases
                for db in env.get('databases', []):
                    db_key = f"db_{db['host']}:{db['port']}/{db['database_name']}"
                    self.health_status[db_key] = self._check_database_health(db)
    
    def _check_url_health(self, url):
        """Check if a URL is healthy"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"URL health check failed for {url}: {e}")
            return False
    
    def _check_database_health(self, db_config):
        """Check if a database is healthy"""
        try:
            port = db_config.get('port', 1433)
            db_type = db_config.get('type', 'primary')
            
            # Determine database type by port or explicit type
            if port == 5432:  # PostgreSQL
                return self._check_postgresql_health(db_config)
            elif port == 3306:  # MySQL
                return self._check_mysql_health(db_config)
            elif port == 1433 or db_config.get('driver') == 'mssql':  # MSSQL
                return self._check_mssql_health(db_config)
            else:
                # Default to MSSQL if no specific port detected
                return self._check_mssql_health(db_config)
        except Exception as e:
            self.logger.debug(f"Database health check failed for {db_config['host']}:{db_config.get('port', 1433)}/{db_config['database_name']}: {e}")
            return False
    
    def _check_postgresql_health(self, db_config):
        """Check PostgreSQL database health"""
        if not PSYCOPG2_AVAILABLE:
            self.logger.warning("psycopg2 not available, skipping PostgreSQL health check")
            return False
        
        try:
            import psycopg2 as pg2
            conn = pg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database_name'],
                user=db_config['username'],
                password=db_config['password'],
                connect_timeout=5
            )
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            conn.close()
            return True
        except Exception as e:
            self.logger.debug(f"PostgreSQL health check failed for {db_config['host']}:{db_config['port']}/{db_config['database_name']}: {e}")
            return False
    
    def _check_mysql_health(self, db_config):
        """Check MySQL database health"""
        if not PYMYSQL_AVAILABLE:
            self.logger.warning("PyMySQL not available, skipping MySQL health check")
            return False
        
        try:
            conn = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database_name'],
                user=db_config['username'],
                password=db_config['password'],
                connect_timeout=5
            )
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            conn.close()
            return True
        except Exception as e:
            self.logger.debug(f"MySQL health check failed for {db_config['host']}:{db_config['port']}/{db_config['database_name']}: {e}")
            return False

    def _check_mssql_health(self, db_config):
        """Check Microsoft SQL Server database health using pyodbc with ODBC Driver 18"""
        if not PYODBC_AVAILABLE:
            self.logger.warning("pyodbc not available, skipping MSSQL health check")
            return False
        
        try:
            # Get available ODBC drivers
            drivers = [driver for driver in pyodbc.drivers() if 'ODBC Driver' in driver and 'for SQL Server' in driver]
            
            if not drivers:
                self.logger.warning("No ODBC drivers found for SQL Server")
                return False
            
            # Use the most recent driver (ODBC Driver 18 preferred)
            driver = drivers[-1]  # Last one is usually the newest
            
            # Build connection string
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={db_config['host']},{db_config.get('port', 1433)};"
                f"DATABASE={db_config['database_name']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=5;"
            )
            
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.debug(f"MSSQL health check failed for {db_config['host']}:{db_config.get('port', 1433)}/{db_config['database_name']}: {e}")
            return False
    
    def get_health_status(self):
        """Get current health status"""
        return self.health_status.copy()
    
    def check_single_service(self, service_key, service_config):
        """Check health of a single service"""
        if service_key.startswith('env_') or service_key.startswith('ms_'):
            return self._check_url_health(service_config)
        elif service_key.startswith('db_'):
            return self._check_database_health(service_config)
        return False