"""
Test configuration management
"""

import unittest
import tempfile
import os
from src.utils.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write("""
kubernetes:
  config_path: ~/.kube/config
  default_namespace: test
  timeout: 30

openai:
  api_key: ${TEST_API_KEY}
  model: gpt-3.5-turbo

output:
  format: json
        """)
        self.temp_config.close()
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_config.name)
    
    def test_load_config(self):
        """Test configuration loading"""
        config = Config(self.temp_config.name)
        
        self.assertEqual(config.get('kubernetes.default_namespace'), 'test')
        self.assertEqual(config.get('kubernetes.timeout'), 30)
        self.assertEqual(config.get('openai.model'), 'gpt-3.5-turbo')
        self.assertEqual(config.get('output.format'), 'json')
    
    def test_get_with_default(self):
        """Test getting value with default"""
        config = Config(self.temp_config.name)
        
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        self.assertIsNone(config.get('nonexistent.key'))
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution"""
        os.environ['TEST_API_KEY'] = 'test-api-key-value'
        config = Config(self.temp_config.name)
        
        self.assertEqual(config.get('openai.api_key'), 'test-api-key-value')
        
        # Clean up
        del os.environ['TEST_API_KEY']
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        config = Config(self.temp_config.name)
        
        config.set('test.new_key', 'new_value')
        self.assertEqual(config.get('test.new_key'), 'new_value')
    
    def test_default_config(self):
        """Test default configuration when file doesn't exist"""
        config = Config('nonexistent.yaml')
        
        self.assertEqual(config.get('kubernetes.default_namespace'), 'default')
        self.assertEqual(config.get('output.format'), 'table')


if __name__ == '__main__':
    unittest.main()
