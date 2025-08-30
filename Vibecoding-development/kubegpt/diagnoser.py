"""
Pod Diagnoser Module

This module handles running kubectl commands and parsing their output
to gather comprehensive information about Kubernetes pods.
"""

import subprocess
import json
import yaml
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PodDiagnoser:
    """
    Handles kubectl operations and pod information gathering
    """
    
    def __init__(self, namespace: str = "default", verbose: bool = False):
        """
        Initialize the diagnoser
        
        Args:
            namespace: Kubernetes namespace to work with
            verbose: Enable verbose logging
        """
        self.namespace = namespace
        self.verbose = verbose
        self._verify_kubectl()
    
    def _verify_kubectl(self) -> None:
        """Verify that kubectl is available and can connect to cluster"""
        try:
            result = self._run_kubectl(["cluster-info"], capture_output=True)
            if self.verbose:
                logger.info("kubectl connection verified")
        except Exception as e:
            raise RuntimeError(f"kubectl not available or cannot connect to cluster: {e}")
    
    def _run_kubectl(self, args: List[str], capture_output: bool = True, timeout: int = 30) -> str:
        """
        Run a kubectl command and return the output
        
        Args:
            args: kubectl command arguments
            capture_output: Whether to capture output
            timeout: Command timeout in seconds
            
        Returns:
            Command output as string
        """
        cmd = ["kubectl"] + args
        
        if self.verbose:
            logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"kubectl command failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"kubectl command timed out after {timeout} seconds")
    
    def diagnose_pod(self, pod_name: str) -> Dict[str, Any]:
        """
        Comprehensive pod diagnosis gathering all relevant information
        
        Args:
            pod_name: Name of the pod to diagnose
            
        Returns:
            Dictionary containing pod information, logs, events, and issues
        """
        pod_data = {
            "name": pod_name,
            "namespace": self.namespace,
            "timestamp": datetime.now().isoformat(),
            "pod_info": {},
            "logs": "",
            "events": [],
            "issues": [],
            "status": "Unknown"
        }
        
        try:
            # Get pod information
            pod_data["pod_info"] = self._get_pod_info(pod_name)
            pod_data["status"] = pod_data["pod_info"].get("status", {}).get("phase", "Unknown")
            
            # Get pod logs (recent)
            pod_data["logs"] = self.get_pod_logs(pod_name, tail=200)
            
            # Get related events
            pod_data["events"] = self.get_events(pod_name, recent=20)
            
            # Analyze for common issues
            pod_data["issues"] = self._detect_common_issues(pod_data)
            
            # Get resource usage if available
            pod_data["resource_usage"] = self._get_resource_usage(pod_name)
            
        except Exception as e:
            logger.error(f"Error diagnosing pod {pod_name}: {e}")
            pod_data["error"] = str(e)
        
        return pod_data
    
    def _get_pod_info(self, pod_name: str) -> Dict[str, Any]:
        """
        Get detailed pod information using kubectl describe and get
        
        Args:
            pod_name: Name of the pod
            
        Returns:
            Dictionary containing pod details
        """
        try:
            # Get pod details in JSON format
            json_output = self._run_kubectl([
                "get", "pod", pod_name,
                "-n", self.namespace,
                "-o", "json"
            ])
            pod_json = json.loads(json_output)
            
            # Get human-readable description
            describe_output = self._run_kubectl([
                "describe", "pod", pod_name,
                "-n", self.namespace
            ])
            
            return {
                "json": pod_json,
                "describe": describe_output,
                "metadata": pod_json.get("metadata", {}),
                "spec": pod_json.get("spec", {}),
                "status": pod_json.get("status", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get pod info for {pod_name}: {e}")
            return {}
    
    def get_pod_logs(self, pod_name: str, container: Optional[str] = None, tail: int = 100) -> str:
        """
        Get pod logs using kubectl logs
        
        Args:
            pod_name: Name of the pod
            container: Specific container name (optional)
            tail: Number of lines to retrieve
            
        Returns:
            Log content as string
        """
        try:
            cmd = ["logs", pod_name, "-n", self.namespace, f"--tail={tail}"]
            
            if container:
                cmd.extend(["-c", container])
            
            # Also try to get previous container logs if current container is restarting
            logs = self._run_kubectl(cmd)
            
            # If the pod is in a restart loop, try to get previous logs too
            try:
                prev_cmd = cmd + ["--previous"]
                prev_logs = self._run_kubectl(prev_cmd)
                if prev_logs:
                    logs = f"=== PREVIOUS CONTAINER LOGS ===\n{prev_logs}\n\n=== CURRENT CONTAINER LOGS ===\n{logs}"
            except:
                # Previous logs might not be available
                pass
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get logs for {pod_name}: {e}")
            return f"Error getting logs: {e}"
    
    def follow_logs(self, pod_name: str, container: Optional[str] = None) -> None:
        """
        Follow pod logs in real-time
        
        Args:
            pod_name: Name of the pod
            container: Specific container name (optional)
        """
        try:
            cmd = ["logs", "-f", pod_name, "-n", self.namespace]
            
            if container:
                cmd.extend(["-c", container])
            
            # Run without capturing output to show logs in real-time
            subprocess.run(["kubectl"] + cmd)
            
        except KeyboardInterrupt:
            print("\nLog following stopped.")
        except Exception as e:
            logger.error(f"Failed to follow logs for {pod_name}: {e}")
    
    def get_events(self, pod_name: Optional[str] = None, recent: int = 20) -> List[Dict[str, Any]]:
        """
        Get Kubernetes events related to the pod or namespace
        
        Args:
            pod_name: Specific pod name (optional)
            recent: Number of recent events to retrieve
            
        Returns:
            List of event dictionaries
        """
        try:
            cmd = ["get", "events", "-n", self.namespace, "--sort-by=.lastTimestamp", "-o", "json"]
            
            events_output = self._run_kubectl(cmd)
            events_json = json.loads(events_output)
            
            events = []
            for event in events_json.get("items", []):
                # Filter by pod name if specified
                if pod_name and event.get("involvedObject", {}).get("name") != pod_name:
                    continue
                
                events.append({
                    "type": event.get("type", "Unknown"),
                    "reason": event.get("reason", ""),
                    "message": event.get("message", ""),
                    "object": f"{event.get('involvedObject', {}).get('kind', '')}/{event.get('involvedObject', {}).get('name', '')}",
                    "first_timestamp": event.get("firstTimestamp", ""),
                    "last_timestamp": event.get("lastTimestamp", ""),
                    "count": event.get("count", 1),
                    "age": self._calculate_age(event.get("lastTimestamp", ""))
                })
            
            # Sort by timestamp (most recent first) and limit
            events.sort(key=lambda x: x["last_timestamp"], reverse=True)
            return events[:recent]
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    def scan_for_problems(self, all_namespaces: bool = False) -> List[Dict[str, Any]]:
        """
        Scan for problematic pods across namespace(s)
        
        Args:
            all_namespaces: Whether to scan all namespaces
            
        Returns:
            List of problematic pod information
        """
        problematic_pods = []
        
        try:
            cmd = ["get", "pods", "-o", "json"]
            
            if all_namespaces:
                cmd.append("--all-namespaces")
            else:
                cmd.extend(["-n", self.namespace])
            
            pods_output = self._run_kubectl(cmd)
            pods_json = json.loads(pods_output)
            
            for pod in pods_json.get("items", []):
                pod_name = pod.get("metadata", {}).get("name", "")
                pod_namespace = pod.get("metadata", {}).get("namespace", "")
                pod_status = pod.get("status", {})
                
                # Check for problematic conditions
                issues = self._analyze_pod_status(pod_status)
                
                if issues:
                    problematic_pods.append({
                        "name": pod_name,
                        "namespace": pod_namespace,
                        "status": pod_status.get("phase", "Unknown"),
                        "issues": issues,
                        "containers": self._analyze_container_statuses(pod_status.get("containerStatuses", []))
                    })
            
        except Exception as e:
            logger.error(f"Failed to scan for problems: {e}")
        
        return problematic_pods
    
    def _get_resource_usage(self, pod_name: str) -> Dict[str, Any]:
        """
        Get resource usage for the pod (requires metrics-server)
        
        Args:
            pod_name: Name of the pod
            
        Returns:
            Resource usage information
        """
        try:
            cmd = ["top", "pod", pod_name, "-n", self.namespace, "--no-headers"]
            output = self._run_kubectl(cmd)
            
            if output:
                parts = output.split()
                if len(parts) >= 3:
                    return {
                        "cpu": parts[1],
                        "memory": parts[2]
                    }
        except Exception:
            # metrics-server might not be available
            pass
        
        return {}
    
    def _detect_common_issues(self, pod_data: Dict[str, Any]) -> List[str]:
        """
        Detect common Kubernetes pod issues
        
        Args:
            pod_data: Pod information dictionary
            
        Returns:
            List of detected issues
        """
        issues = []
        
        try:
            pod_status = pod_data.get("pod_info", {}).get("status", {})
            pod_phase = pod_status.get("phase", "")
            
            # Check pod phase
            if pod_phase in ["Failed", "Pending"]:
                issues.append(f"Pod is in {pod_phase} state")
            
            # Check container statuses
            container_statuses = pod_status.get("containerStatuses", [])
            for container in container_statuses:
                state = container.get("state", {})
                
                # CrashLoopBackOff
                if "waiting" in state and state["waiting"].get("reason") == "CrashLoopBackOff":
                    issues.append(f"Container {container.get('name')} is in CrashLoopBackOff")
                
                # ImagePullBackOff / ErrImagePull
                if "waiting" in state and state["waiting"].get("reason") in ["ImagePullBackOff", "ErrImagePull"]:
                    issues.append(f"Container {container.get('name')} has image pull issues")
                
                # OOMKilled
                if "terminated" in state and state["terminated"].get("reason") == "OOMKilled":
                    issues.append(f"Container {container.get('name')} was killed due to OOM (Out of Memory)")
                
                # High restart count
                restart_count = container.get("restartCount", 0)
                if restart_count > 5:
                    issues.append(f"Container {container.get('name')} has high restart count: {restart_count}")
            
            # Check events for additional issues
            events = pod_data.get("events", [])
            for event in events:
                if event.get("type") == "Warning":
                    reason = event.get("reason", "")
                    if reason in ["Failed", "FailedScheduling", "FailedMount"]:
                        issues.append(f"Warning event: {reason} - {event.get('message', '')}")
            
            # Check logs for errors
            logs = pod_data.get("logs", "")
            if self._has_error_patterns_in_logs(logs):
                issues.append("Error patterns detected in logs")
                
        except Exception as e:
            logger.error(f"Error detecting issues: {e}")
        
        return issues
    
    def _analyze_pod_status(self, pod_status: Dict[str, Any]) -> List[str]:
        """Analyze pod status for issues"""
        issues = []
        
        phase = pod_status.get("phase", "")
        if phase in ["Failed", "Pending"]:
            issues.append(f"Pod in {phase} state")
        
        # Check conditions
        conditions = pod_status.get("conditions", [])
        for condition in conditions:
            if condition.get("status") == "False" and condition.get("type") in ["Ready", "PodScheduled"]:
                issues.append(f"{condition.get('type')} condition is False: {condition.get('message', '')}")
        
        return issues
    
    def _analyze_container_statuses(self, container_statuses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze container statuses for issues"""
        containers = []
        
        for container in container_statuses:
            container_info = {
                "name": container.get("name", ""),
                "ready": container.get("ready", False),
                "restart_count": container.get("restartCount", 0),
                "state": container.get("state", {}),
                "issues": []
            }
            
            state = container.get("state", {})
            if "waiting" in state:
                reason = state["waiting"].get("reason", "")
                if reason in ["CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"]:
                    container_info["issues"].append(f"Waiting: {reason}")
            
            if "terminated" in state:
                reason = state["terminated"].get("reason", "")
                if reason == "OOMKilled":
                    container_info["issues"].append("Terminated: OOMKilled")
            
            containers.append(container_info)
        
        return containers
    
    def _has_error_patterns_in_logs(self, logs: str) -> bool:
        """Check logs for common error patterns"""
        error_patterns = [
            r"error|Error|ERROR",
            r"exception|Exception|EXCEPTION", 
            r"fatal|Fatal|FATAL",
            r"panic|Panic|PANIC",
            r"failed|Failed|FAILED",
            r"timeout|Timeout|TIMEOUT"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, logs):
                return True
        
        return False
    
    def _calculate_age(self, timestamp: str) -> str:
        """Calculate age from timestamp"""
        try:
            if not timestamp:
                return "Unknown"
            
            # Parse the timestamp (handle different formats)
            from datetime import datetime
            import dateutil.parser
            
            event_time = dateutil.parser.parse(timestamp)
            now = datetime.now(event_time.tzinfo)
            
            age = now - event_time
            
            if age.days > 0:
                return f"{age.days}d"
            elif age.seconds > 3600:
                return f"{age.seconds // 3600}h"
            elif age.seconds > 60:
                return f"{age.seconds // 60}m"
            else:
                return f"{age.seconds}s"
        except:
            return "Unknown"
