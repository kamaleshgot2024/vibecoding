"""
Test configuration and utilities
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from src.utils.config import Config


class TestKubeGPT(unittest.TestCase):
    """Base test class for KubeGPT tests"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write("""
kubernetes:
  config_path: ~/.kube/config
  default_namespace: test
  timeout: 30

openai:
  api_key: test-key
  model: gpt-3.5-turbo
  max_tokens: 500

output:
  format: json
  color: false

logging:
  level: DEBUG
  file: test.log
        """)
        self.temp_config.close()
        
        self.config = Config(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_config.name)


def create_mock_pod():
    """Create a mock Kubernetes pod object"""
    mock_pod = Mock()
    mock_pod.metadata.name = "test-pod"
    mock_pod.metadata.namespace = "default"
    mock_pod.metadata.creation_timestamp = "2023-01-01T00:00:00Z"
    mock_pod.metadata.labels = {"app": "test"}
    mock_pod.metadata.annotations = {}
    
    mock_pod.status.phase = "Running"
    mock_pod.status.conditions = []
    mock_pod.status.container_statuses = []
    
    mock_pod.spec.node_name = "test-node"
    mock_pod.spec.containers = []
    
    return mock_pod


def create_mock_event():
    """Create a mock Kubernetes event object"""
    mock_event = Mock()
    mock_event.type = "Normal"
    mock_event.reason = "Started"
    mock_event.message = "Container started"
    mock_event.first_timestamp = "2023-01-01T00:00:00Z"
    mock_event.last_timestamp = "2023-01-01T00:00:00Z"
    mock_event.count = 1
    mock_event.source.component = "kubelet"
    mock_event.involved_object.kind = "Pod"
    mock_event.involved_object.name = "test-pod"
    
    return mock_event
