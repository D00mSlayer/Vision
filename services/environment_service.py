"""
Environment Service Module
Handles loading and managing environment data from YAML files
"""

import yaml
import logging
import os


class EnvironmentService:
    """Service for managing environment data"""
    
    def __init__(self):
        self.data_file = 'data/environments.yaml'
        self.environment_data = None
        self.logger = logging.getLogger(__name__)
        self._load_data()
    
    def _load_data(self):
        """Load environment data from YAML file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as file:
                    self.environment_data = yaml.safe_load(file)
                self.logger.info("Environment data loaded successfully")
            else:
                self.logger.error(f"Environment data file not found: {self.data_file}")
                self.environment_data = {"product_versions": []}
        except Exception as e:
            self.logger.error(f"Error loading environment data: {e}")
            self.environment_data = {"product_versions": []}
    
    def get_environment_data(self):
        """Get current environment data"""
        if self.environment_data is None:
            self._load_data()
        return self.environment_data
    
    def reload_data(self):
        """Reload environment data from file"""
        self._load_data()
        return self.environment_data