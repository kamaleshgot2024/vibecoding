"""
Configuration management for KubeGPT
"""

import os
import yaml
import logging
from typing import Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for KubeGPT"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """Initialize configuration from file"""
        self.config_file = config_file
        self.config_data = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")
                self.config_data = self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config_data = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'kubernetes.namespace')"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            
            # Handle environment variable substitution
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                return env_value if env_value is not None else default
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'kubernetes': {
                'config_path': '~/.kube/config',
                'default_namespace': 'default',
                'timeout': 30
            },
            'openai': {
                'api_key': '${OPENAI_API_KEY}',
                'model': 'gpt-3.5-turbo',
                'max_tokens': 1000,
                'temperature': 0.3
            },
            'output': {
                'format': 'table',
                'color': True,
                'max_log_lines': 100
            },
            'logging': {
                'level': 'INFO',
                'file': 'kubegpt.log'
            }
        }
    
    def get_kubernetes_config_path(self) -> str:
        """Get expanded Kubernetes config path"""
        path = self.get('kubernetes.config_path', '~/.kube/config')
        return os.path.expanduser(path)
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key with environment variable support"""
        return self.get('openai.api_key')
    
    def is_ai_enabled(self) -> bool:
        """Check if AI features are enabled"""
        return self.get_openai_api_key() is not None
    
    def get_log_level(self) -> str:
        """Get logging level"""
        return self.get('logging.level', 'INFO').upper()
    
    def get_log_file(self) -> str:
        """Get log file path"""
        return self.get('logging.file', 'kubegpt.log')
