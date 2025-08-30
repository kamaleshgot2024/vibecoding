"""
Test Kubernetes client functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from src.kubernetes.kubernetes_client import KubernetesClient
from tests.test_utils import TestKubeGPT, create_mock_pod, create_mock_event


class TestKubernetesClient(TestKubeGPT):
    """Test Kubernetes client"""
    
    @patch('src.kubernetes.kubernetes_client.config')
    @patch('src.kubernetes.kubernetes_client.client')
    def setUp(self, mock_client, mock_config):
        """Set up test environment"""
        super().setUp()
        
        # Mock Kubernetes API clients
        self.mock_v1 = Mock()
        mock_client.CoreV1Api.return_value = self.mock_v1
        
        self.mock_apps_v1 = Mock()
        mock_client.AppsV1Api.return_value = self.mock_apps_v1
        
        # Initialize client
        self.k8s_client = KubernetesClient(self.config)
    
    def test_get_pod_info(self):
        """Test getting pod information"""
        # Create mock pod
        mock_pod = create_mock_pod()
        mock_pod.metadata.creation_timestamp = datetime.now(timezone.utc)
        
        self.mock_v1.read_namespaced_pod.return_value = mock_pod
        
        # Test
        pod_info = self.k8s_client.get_pod_info("test-pod", "default")
        
        self.assertEqual(pod_info['name'], "test-pod")
        self.assertEqual(pod_info['namespace'], "default")
        self.assertEqual(pod_info['status'], "Running")
        self.assertEqual(pod_info['node'], "test-node")
    
    def test_get_pod_logs(self):
        """Test getting pod logs"""
        mock_logs = "2023-01-01 INFO: Application started\n2023-01-01 ERROR: Something failed"
        self.mock_v1.read_namespaced_pod_log.return_value = mock_logs
        
        logs = self.k8s_client.get_pod_logs("test-pod", "default")
        
        self.assertEqual(logs, mock_logs)
        self.mock_v1.read_namespaced_pod_log.assert_called_once()
    
    def test_get_pod_events(self):
        """Test getting pod events"""
        # Create mock events
        mock_event = create_mock_event()
        mock_events = Mock()
        mock_events.items = [mock_event]
        
        self.mock_v1.list_namespaced_event.return_value = mock_events
        
        events = self.k8s_client.get_pod_events("test-pod", "default")
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], "Normal")
        self.assertEqual(events[0]['reason'], "Started")
    
    def test_list_pods(self):
        """Test listing pods"""
        # Create mock pod list
        mock_pod = create_mock_pod()
        mock_pod.metadata.creation_timestamp = datetime.now(timezone.utc)
        
        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        
        self.mock_v1.list_namespaced_pod.return_value = mock_pods
        
        pods = self.k8s_client.list_pods("default")
        
        self.assertEqual(len(pods), 1)
        self.assertEqual(pods[0]['name'], "test-pod")
        self.assertEqual(pods[0]['status'], "Running")
    
    def test_get_namespace_health(self):
        """Test getting namespace health"""
        # Create mock pods with different statuses
        running_pod = create_mock_pod()
        running_pod.metadata.name = "running-pod"
        running_pod.status.phase = "Running"
        
        failed_pod = create_mock_pod()
        failed_pod.metadata.name = "failed-pod"
        failed_pod.status.phase = "Failed"
        
        mock_pods = Mock()
        mock_pods.items = [running_pod, failed_pod]
        
        self.mock_v1.list_namespaced_pod.return_value = mock_pods
        
        health = self.k8s_client.get_namespace_health("default")
        
        self.assertEqual(health['total_pods'], 2)
        self.assertEqual(health['running_pods'], 1)
        self.assertEqual(health['failed_pods'], 1)
        self.assertEqual(health['health_score'], 50.0)


if __name__ == '__main__':
    unittest.main()
