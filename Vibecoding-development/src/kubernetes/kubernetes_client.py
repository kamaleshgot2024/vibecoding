"""
Kubernetes Client for KubeGPT

Handles all Kubernetes API interactions including:
- Pod information retrieval
- Log collection
- Event monitoring
- Resource status checking
"""

import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import logging

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Client for interacting with Kubernetes API"""
    
    def __init__(self, app_config):
        """Initialize Kubernetes client with configuration"""
        self.config = app_config
        self._load_kube_config()
        self._initialize_clients()
    
    def _load_kube_config(self):
        """Load Kubernetes configuration"""
        try:
            # Try to load in-cluster config first (if running in a pod)
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except:
            try:
                # Load from kubeconfig file
                config_path = self.config.get('kubernetes.config_path', '~/.kube/config')
                config_path = os.path.expanduser(config_path)
                config.load_kube_config(config_file=config_path)
                logger.info(f"Loaded Kubernetes configuration from {config_path}")
            except Exception as e:
                raise Exception(f"Failed to load Kubernetes configuration: {e}")
    
    def _initialize_clients(self):
        """Initialize Kubernetes API clients"""
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.extensions_v1beta1 = client.ExtensionsV1beta1Api()
    
    def get_pod_info(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Get detailed information about a specific pod"""
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            # Calculate age
            created_time = pod.metadata.creation_timestamp
            age = self._calculate_age(created_time)
            
            # Get container statuses
            container_statuses = []
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_statuses.append({
                        'name': container_status.name,
                        'ready': container_status.ready,
                        'restart_count': container_status.restart_count,
                        'state': self._get_container_state(container_status.state)
                    })
            
            # Get resource requests and limits
            resources = self._get_pod_resources(pod)
            
            return {
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': pod.status.phase,
                'node': pod.spec.node_name or 'Not Scheduled',
                'created': created_time.isoformat() if created_time else 'Unknown',
                'age': age,
                'containers': container_statuses,
                'resources': resources,
                'labels': pod.metadata.labels or {},
                'annotations': pod.metadata.annotations or {},
                'conditions': self._get_pod_conditions(pod.status.conditions)
            }
        except ApiException as e:
            if e.status == 404:
                raise Exception(f"Pod '{pod_name}' not found in namespace '{namespace}'")
            else:
                raise Exception(f"Error getting pod info: {e}")
    
    def get_pod_logs(self, pod_name: str, namespace: str, container: Optional[str] = None, 
                     tail: int = 100, follow: bool = False) -> str:
        """Get logs from a pod"""
        try:
            kwargs = {
                'name': pod_name,
                'namespace': namespace,
                'tail_lines': tail,
                'timestamps': True
            }
            
            if container:
                kwargs['container'] = container
            
            if follow:
                kwargs['follow'] = True
                
            logs = self.v1.read_namespaced_pod_log(**kwargs)
            return logs
        except ApiException as e:
            if e.status == 404:
                raise Exception(f"Pod '{pod_name}' not found in namespace '{namespace}'")
            else:
                raise Exception(f"Error getting pod logs: {e}")
    
    def follow_pod_logs(self, pod_name: str, namespace: str, container: Optional[str] = None):
        """Follow pod logs in real-time"""
        try:
            kwargs = {
                'name': pod_name,
                'namespace': namespace,
                'follow': True,
                'timestamps': True
            }
            
            if container:
                kwargs['container'] = container
            
            w = watch.Watch()
            for line in w.stream(self.v1.read_namespaced_pod_log, **kwargs):
                print(line)
                
        except KeyboardInterrupt:
            print("\nLog following stopped.")
        except ApiException as e:
            raise Exception(f"Error following pod logs: {e}")
    
    def get_pod_events(self, pod_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get events related to a specific pod"""
        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            pod_events = []
            
            for event in events.items:
                if (event.involved_object.name == pod_name and 
                    event.involved_object.kind == 'Pod'):
                    pod_events.append({
                        'type': event.type,
                        'reason': event.reason,
                        'message': event.message,
                        'first_timestamp': event.first_timestamp.isoformat() if event.first_timestamp else None,
                        'last_timestamp': event.last_timestamp.isoformat() if event.last_timestamp else None,
                        'count': event.count,
                        'source': event.source.component if event.source else 'Unknown',
                        'object': f"{event.involved_object.kind}/{event.involved_object.name}",
                        'age': self._calculate_age(event.first_timestamp)
                    })
            
            # Sort by timestamp (most recent first)
            pod_events.sort(key=lambda x: x['last_timestamp'] or x['first_timestamp'], reverse=True)
            return pod_events
            
        except ApiException as e:
            raise Exception(f"Error getting pod events: {e}")
    
    def get_namespace_events(self, namespace: str) -> List[Dict[str, Any]]:
        """Get all events in a namespace"""
        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            namespace_events = []
            
            for event in events.items:
                namespace_events.append({
                    'type': event.type,
                    'reason': event.reason,
                    'message': event.message,
                    'first_timestamp': event.first_timestamp.isoformat() if event.first_timestamp else None,
                    'last_timestamp': event.last_timestamp.isoformat() if event.last_timestamp else None,
                    'count': event.count,
                    'source': event.source.component if event.source else 'Unknown',
                    'object': f"{event.involved_object.kind}/{event.involved_object.name}",
                    'age': self._calculate_age(event.first_timestamp)
                })
            
            # Sort by timestamp (most recent first)
            namespace_events.sort(key=lambda x: x['last_timestamp'] or x['first_timestamp'], reverse=True)
            return namespace_events[:50]  # Limit to recent 50 events
            
        except ApiException as e:
            raise Exception(f"Error getting namespace events: {e}")
    
    def list_pods(self, namespace: str) -> List[Dict[str, Any]]:
        """List all pods in a namespace"""
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            pod_list = []
            
            for pod in pods.items:
                # Calculate ready containers
                ready_count = 0
                total_count = 0
                restart_count = 0
                
                if pod.status.container_statuses:
                    total_count = len(pod.status.container_statuses)
                    for container_status in pod.status.container_statuses:
                        if container_status.ready:
                            ready_count += 1
                        restart_count += container_status.restart_count
                
                pod_list.append({
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase,
                    'ready': f"{ready_count}/{total_count}",
                    'restarts': restart_count,
                    'age': self._calculate_age(pod.metadata.creation_timestamp),
                    'node': pod.spec.node_name or 'Not Scheduled'
                })
            
            return pod_list
            
        except ApiException as e:
            raise Exception(f"Error listing pods: {e}")
    
    def get_namespace_health(self, namespace: str) -> Dict[str, Any]:
        """Get comprehensive health information for a namespace"""
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            
            total_pods = len(pods.items)
            running_pods = 0
            failed_pods = 0
            pending_pods = 0
            failed_pod_details = []
            
            for pod in pods.items:
                status = pod.status.phase
                
                if status == 'Running':
                    running_pods += 1
                elif status in ['Failed', 'CrashLoopBackOff']:
                    failed_pods += 1
                    failed_pod_details.append({
                        'name': pod.metadata.name,
                        'status': status,
                        'reason': self._get_pod_failure_reason(pod)
                    })
                elif status == 'Pending':
                    pending_pods += 1
            
            return {
                'namespace': namespace,
                'total_pods': total_pods,
                'running_pods': running_pods,
                'failed_pods': failed_pods,
                'pending_pods': pending_pods,
                'failed_pod_details': failed_pod_details,
                'health_score': (running_pods / total_pods * 100) if total_pods > 0 else 0
            }
            
        except ApiException as e:
            raise Exception(f"Error getting namespace health: {e}")
    
    def _calculate_age(self, created_time) -> str:
        """Calculate age from creation timestamp"""
        if not created_time:
            return "Unknown"
        
        now = datetime.now(timezone.utc)
        age = now - created_time
        
        if age.days > 0:
            return f"{age.days}d"
        elif age.seconds > 3600:
            return f"{age.seconds // 3600}h"
        elif age.seconds > 60:
            return f"{age.seconds // 60}m"
        else:
            return f"{age.seconds}s"
    
    def _get_container_state(self, state) -> str:
        """Get human-readable container state"""
        if state.running:
            return "Running"
        elif state.waiting:
            return f"Waiting: {state.waiting.reason}"
        elif state.terminated:
            return f"Terminated: {state.terminated.reason}"
        else:
            return "Unknown"
    
    def _get_pod_resources(self, pod) -> Dict[str, Any]:
        """Extract resource requests and limits from pod"""
        resources = {
            'requests': {'cpu': '0', 'memory': '0'},
            'limits': {'cpu': '0', 'memory': '0'}
        }
        
        for container in pod.spec.containers:
            if container.resources:
                if container.resources.requests:
                    if 'cpu' in container.resources.requests:
                        resources['requests']['cpu'] = container.resources.requests['cpu']
                    if 'memory' in container.resources.requests:
                        resources['requests']['memory'] = container.resources.requests['memory']
                
                if container.resources.limits:
                    if 'cpu' in container.resources.limits:
                        resources['limits']['cpu'] = container.resources.limits['cpu']
                    if 'memory' in container.resources.limits:
                        resources['limits']['memory'] = container.resources.limits['memory']
        
        return resources
    
    def _get_pod_conditions(self, conditions) -> List[Dict[str, Any]]:
        """Extract pod conditions"""
        if not conditions:
            return []
        
        condition_list = []
        for condition in conditions:
            condition_list.append({
                'type': condition.type,
                'status': condition.status,
                'reason': condition.reason,
                'message': condition.message,
                'last_transition_time': condition.last_transition_time.isoformat() if condition.last_transition_time else None
            })
        
        return condition_list
    
    def _get_pod_failure_reason(self, pod) -> str:
        """Get reason for pod failure"""
        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if container_status.state.waiting:
                    return container_status.state.waiting.reason
                elif container_status.state.terminated:
                    return container_status.state.terminated.reason
        
        if pod.status.conditions:
            for condition in pod.status.conditions:
                if condition.type == 'PodScheduled' and condition.status == 'False':
                    return condition.reason or 'SchedulingFailed'
        
        return "Unknown"
