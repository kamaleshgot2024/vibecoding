"""
Fix Recommender Module

This module analyzes pod issues and suggests fixes based on known patterns
and best practices. It provides actionable kubectl commands and YAML suggestions.
"""

import re
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FixRecommender:
    """
    Analyzes pod issues and recommends specific fixes based on known patterns
    
    This class contains expert knowledge about common Kubernetes issues
    and their solutions, providing actionable kubectl commands and YAML patches.
    """
    
    def __init__(self):
        """Initialize the fix recommender with known issue patterns"""
        self.issue_patterns = self._initialize_issue_patterns()
        self.fix_templates = self._initialize_fix_templates()
    
    def analyze_and_recommend(self, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pod data and recommend comprehensive fixes
        
        Args:
            pod_data: Complete pod information from diagnoser
            
        Returns:
            Dictionary containing recommendations, commands, and YAML suggestions
        """
        recommendations = {
            "summary": "",
            "issues_analyzed": [],
            "commands": [],
            "yaml_patches": [],
            "quick_fixes": [],
            "preventive_measures": [],
            "confidence_score": 0.0
        }
        
        try:
            # Analyze each detected issue
            issues = pod_data.get("issues", [])
            pod_info = pod_data.get("pod_info", {})
            logs = pod_data.get("logs", "")
            events = pod_data.get("events", [])
            
            for issue in issues:
                issue_analysis = self._analyze_specific_issue(issue, pod_data)
                recommendations["issues_analyzed"].append(issue_analysis)
                
                # Add commands and fixes
                if issue_analysis.get("commands"):
                    recommendations["commands"].extend(issue_analysis["commands"])
                
                if issue_analysis.get("yaml_patch"):
                    recommendations["yaml_patches"].append(issue_analysis["yaml_patch"])
                
                if issue_analysis.get("quick_fixes"):
                    recommendations["quick_fixes"].extend(issue_analysis["quick_fixes"])
            
            # Analyze logs for additional insights
            log_recommendations = self._analyze_logs_for_fixes(logs, pod_data)
            if log_recommendations:
                recommendations["commands"].extend(log_recommendations.get("commands", []))
                recommendations["quick_fixes"].extend(log_recommendations.get("fixes", []))
            
            # Add general diagnostic commands
            recommendations["commands"].extend(self._get_diagnostic_commands(pod_data))
            
            # Generate summary
            recommendations["summary"] = self._generate_summary(recommendations)
            
            # Calculate confidence score
            recommendations["confidence_score"] = self._calculate_confidence_score(recommendations)
            
        except Exception as e:
            logger.error(f"Error in analyze_and_recommend: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    def generate_fixes(self, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate specific fixes for the pod issues
        
        Args:
            pod_data: Pod information
            
        Returns:
            Dictionary containing detailed fix instructions
        """
        fixes = {
            "immediate_actions": [],
            "configuration_changes": [],
            "yaml_patches": [],
            "kubectl_commands": [],
            "validation_steps": []
        }
        
        issues = pod_data.get("issues", [])
        
        for issue in issues:
            issue_fixes = self._get_fixes_for_issue(issue, pod_data)
            
            fixes["immediate_actions"].extend(issue_fixes.get("immediate", []))
            fixes["configuration_changes"].extend(issue_fixes.get("config", []))
            fixes["yaml_patches"].extend(issue_fixes.get("yaml", []))
            fixes["kubectl_commands"].extend(issue_fixes.get("commands", []))
            fixes["validation_steps"].extend(issue_fixes.get("validation", []))
        
        return fixes
    
    def get_quick_fixes(self, pod_info: Dict[str, Any]) -> List[str]:
        """
        Get quick fix suggestions for a pod
        
        Args:
            pod_info: Basic pod information
            
        Returns:
            List of quick fix suggestions
        """
        quick_fixes = []
        issues = pod_info.get("issues", [])
        
        for issue in issues:
            if "crashloopbackoff" in issue.lower():
                quick_fixes.append("Check logs for startup errors: kubectl logs <pod> --previous")
                quick_fixes.append("Verify resource limits are not too restrictive")
            
            elif "imagepull" in issue.lower():
                quick_fixes.append("Verify image name and tag are correct")
                quick_fixes.append("Check registry access and credentials")
            
            elif "oom" in issue.lower():
                quick_fixes.append("Increase memory limits in pod specification")
                quick_fixes.append("Review application memory usage patterns")
            
            elif "pending" in issue.lower():
                quick_fixes.append("Check node resources: kubectl describe nodes")
                quick_fixes.append("Verify scheduling constraints and tolerations")
        
        return quick_fixes
    
    def analyze_logs(self, logs: str) -> str:
        """
        Analyze logs and provide insights
        
        Args:
            logs: Pod log content
            
        Returns:
            Log analysis summary
        """
        analysis = "## 📝 Log Analysis\n\n"
        
        # Check for common error patterns
        error_patterns = {
            r"out of memory|oom|OutOfMemoryError": "Memory issues detected - consider increasing memory limits",
            r"connection refused|connection timeout": "Network connectivity issues detected",
            r"permission denied|access denied": "Permission/security issues detected",
            r"no space left|disk full": "Disk space issues detected",
            r"image.*not found|pull.*failed": "Container image issues detected",
            r"port.*already in use|address already in use": "Port conflict detected",
            r"failed to start|startup failed|initialization failed": "Application startup issues detected"
        }
        
        found_patterns = []
        for pattern, description in error_patterns.items():
            if re.search(pattern, logs, re.IGNORECASE):
                found_patterns.append(f"• {description}")
        
        if found_patterns:
            analysis += "**Issues Found in Logs:**\n" + "\n".join(found_patterns) + "\n\n"
        else:
            analysis += "**No obvious error patterns found in logs.**\n\n"
        
        # Extract recent error lines
        error_lines = []
        for line in logs.split('\n')[-50:]:  # Check last 50 lines
            if re.search(r"error|exception|fatal|panic", line, re.IGNORECASE):
                error_lines.append(line.strip())
        
        if error_lines:
            analysis += "**Recent Error Lines:**\n"
            for line in error_lines[-5:]:  # Show last 5 error lines
                analysis += f"```\n{line}\n```\n"
        
        return analysis
    
    def _analyze_specific_issue(self, issue: str, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific issue and provide targeted recommendations"""
        pod_name = pod_data.get("name", "unknown")
        namespace = pod_data.get("namespace", "default")
        
        issue_analysis = {
            "issue": issue,
            "severity": "medium",
            "commands": [],
            "yaml_patch": "",
            "quick_fixes": [],
            "explanation": ""
        }
        
        issue_lower = issue.lower()
        
        # CrashLoopBackOff analysis
        if "crashloopbackoff" in issue_lower:
            issue_analysis.update({
                "severity": "high",
                "commands": [
                    f"kubectl logs {pod_name} -n {namespace} --previous",
                    f"kubectl describe pod {pod_name} -n {namespace}",
                    f"kubectl get pod {pod_name} -n {namespace} -o yaml"
                ],
                "quick_fixes": [
                    "Check previous container logs for startup errors",
                    "Verify application configuration and environment variables",
                    "Review resource limits and requests",
                    "Check liveness and readiness probe configurations"
                ],
                "explanation": "Pod is crashing repeatedly. This usually indicates application startup issues, configuration problems, or resource constraints.",
                "yaml_patch": self._generate_crashloop_yaml_patch(pod_data)
            })
        
        # ImagePull issues
        elif "imagepull" in issue_lower:
            issue_analysis.update({
                "severity": "high",
                "commands": [
                    f"kubectl describe pod {pod_name} -n {namespace}",
                    "kubectl get events -n {namespace} --sort-by=.lastTimestamp",
                    f"kubectl get pod {pod_name} -n {namespace} -o jsonpath='{{.spec.containers[*].image}}'"
                ],
                "quick_fixes": [
                    "Verify image name and tag are correct",
                    "Check registry credentials and access",
                    "Ensure registry is accessible from cluster",
                    "Try pulling image manually: docker pull <image>"
                ],
                "explanation": "Cannot pull container image. Check image name, registry access, and credentials.",
                "yaml_patch": self._generate_imagepull_yaml_patch(pod_data)
            })
        
        # OOM (Out of Memory) issues
        elif "oom" in issue_lower:
            issue_analysis.update({
                "severity": "high",
                "commands": [
                    f"kubectl describe pod {pod_name} -n {namespace}",
                    f"kubectl top pod {pod_name} -n {namespace}",
                    f"kubectl logs {pod_name} -n {namespace} --previous"
                ],
                "quick_fixes": [
                    "Increase memory limits in pod specification",
                    "Review application memory usage and optimize if possible",
                    "Check for memory leaks in application",
                    "Consider using memory profiling tools"
                ],
                "explanation": "Container was killed due to out of memory. Increase memory limits or optimize application memory usage.",
                "yaml_patch": self._generate_memory_yaml_patch(pod_data)
            })
        
        # Pending state issues
        elif "pending" in issue_lower:
            issue_analysis.update({
                "severity": "medium",
                "commands": [
                    f"kubectl describe pod {pod_name} -n {namespace}",
                    "kubectl describe nodes",
                    "kubectl get events -n {namespace}",
                    f"kubectl get pod {pod_name} -n {namespace} -o yaml"
                ],
                "quick_fixes": [
                    "Check node resources and availability",
                    "Verify scheduling constraints (nodeSelector, affinity)",
                    "Check persistent volume claims if used",
                    "Review resource requests vs available node capacity"
                ],
                "explanation": "Pod cannot be scheduled. Usually due to insufficient resources, scheduling constraints, or node issues.",
                "yaml_patch": self._generate_scheduling_yaml_patch(pod_data)
            })
        
        return issue_analysis
    
    def _analyze_logs_for_fixes(self, logs: str, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze logs and suggest specific fixes"""
        pod_name = pod_data.get("name", "unknown")
        namespace = pod_data.get("namespace", "default")
        
        recommendations = {
            "commands": [],
            "fixes": []
        }
        
        if not logs:
            return recommendations
        
        # Specific log pattern analysis
        if re.search(r"port.*already in use|address.*already in use", logs, re.IGNORECASE):
            recommendations["fixes"].append("Port conflict detected - check for duplicate services")
            recommendations["commands"].append(f"kubectl get svc -n {namespace}")
        
        if re.search(r"connection refused|connection timeout", logs, re.IGNORECASE):
            recommendations["fixes"].append("Network connectivity issues - check service endpoints")
            recommendations["commands"].extend([
                f"kubectl get endpoints -n {namespace}",
                f"kubectl describe svc -n {namespace}"
            ])
        
        if re.search(r"permission denied|access denied", logs, re.IGNORECASE):
            recommendations["fixes"].append("Permission issues - check RBAC and security context")
            recommendations["commands"].extend([
                f"kubectl describe pod {pod_name} -n {namespace}",
                f"kubectl get rolebindings,clusterrolebindings -n {namespace}"
            ])
        
        if re.search(r"disk.*full|no space left", logs, re.IGNORECASE):
            recommendations["fixes"].append("Disk space issues - check node disk usage")
            recommendations["commands"].append("kubectl describe nodes")
        
        return recommendations
    
    def _get_fixes_for_issue(self, issue: str, pod_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get detailed fixes for a specific issue"""
        pod_name = pod_data.get("name", "unknown")
        namespace = pod_data.get("namespace", "default")
        
        fixes = {
            "immediate": [],
            "config": [],
            "yaml": [],
            "commands": [],
            "validation": []
        }
        
        issue_lower = issue.lower()
        
        if "crashloopbackoff" in issue_lower:
            fixes.update({
                "immediate": [
                    "Check previous container logs for error messages",
                    "Verify application startup sequence and dependencies"
                ],
                "config": [
                    "Review environment variables and configuration files",
                    "Check resource limits and requests",
                    "Validate liveness and readiness probe settings"
                ],
                "commands": [
                    f"kubectl logs {pod_name} -n {namespace} --previous",
                    f"kubectl edit deployment <deployment-name> -n {namespace}"
                ],
                "validation": [
                    f"kubectl get pod {pod_name} -n {namespace} -w",
                    f"kubectl describe pod {pod_name} -n {namespace}"
                ]
            })
        
        elif "imagepull" in issue_lower:
            fixes.update({
                "immediate": [
                    "Verify container image name and tag",
                    "Check registry accessibility"
                ],
                "config": [
                    "Update image pull secrets if using private registry",
                    "Verify image exists in the specified registry"
                ],
                "commands": [
                    f"kubectl create secret docker-registry <secret-name> --docker-server=<server> --docker-username=<username> --docker-password=<password>",
                    f"kubectl patch pod {pod_name} -n {namespace} -p '{{\"spec\":{{\"imagePullSecrets\":[{{\"name\":\"<secret-name>\"}}]}}}}'"
                ],
                "validation": [
                    f"kubectl describe pod {pod_name} -n {namespace}",
                    "docker pull <image-name>"
                ]
            })
        
        return fixes
    
    def _get_diagnostic_commands(self, pod_data: Dict[str, Any]) -> List[str]:
        """Get general diagnostic commands for the pod"""
        pod_name = pod_data.get("name", "unknown")
        namespace = pod_data.get("namespace", "default")
        
        return [
            f"# Basic pod information",
            f"kubectl get pod {pod_name} -n {namespace} -o wide",
            f"kubectl describe pod {pod_name} -n {namespace}",
            f"",
            f"# Logs and events",
            f"kubectl logs {pod_name} -n {namespace}",
            f"kubectl get events -n {namespace} --sort-by=.lastTimestamp",
            f"",
            f"# Resource usage (if metrics-server available)",
            f"kubectl top pod {pod_name} -n {namespace}",
            f"",
            f"# Network debugging",
            f"kubectl get svc,endpoints -n {namespace}",
            f"kubectl describe node $(kubectl get pod {pod_name} -n {namespace} -o jsonpath='{{.spec.nodeName}}')"
        ]
    
    def _generate_crashloop_yaml_patch(self, pod_data: Dict[str, Any]) -> str:
        """Generate YAML patch for CrashLoopBackOff issues"""
        return """
# Potential fixes for CrashLoopBackOff:

1. Increase resource limits:
spec:
  containers:
  - name: <container-name>
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
      requests:
        memory: "256Mi" 
        cpu: "250m"

2. Adjust probe timings:
spec:
  containers:
  - name: <container-name>
    livenessProbe:
      initialDelaySeconds: 60
      periodSeconds: 30
      timeoutSeconds: 10
    readinessProbe:
      initialDelaySeconds: 30
      periodSeconds: 15

3. Add debug command (temporary):
spec:
  containers:
  - name: <container-name>
    command: ["/bin/sh"]
    args: ["-c", "sleep 3600"]  # Keep container running for debugging
"""
    
    def _generate_imagepull_yaml_patch(self, pod_data: Dict[str, Any]) -> str:
        """Generate YAML patch for image pull issues"""
        return """
# Fixes for image pull issues:

1. Add image pull secrets:
spec:
  imagePullSecrets:
  - name: <registry-secret>

2. Use specific image tag (avoid 'latest'):
spec:
  containers:
  - name: <container-name>
    image: <registry>/<image>:<specific-tag>
    imagePullPolicy: IfNotPresent

3. Create registry secret:
kubectl create secret docker-registry <secret-name> \\
  --docker-server=<registry-url> \\
  --docker-username=<username> \\
  --docker-password=<password> \\
  --docker-email=<email>
"""
    
    def _generate_memory_yaml_patch(self, pod_data: Dict[str, Any]) -> str:
        """Generate YAML patch for memory issues"""
        return """
# Fixes for OOM (Out of Memory) issues:

1. Increase memory limits:
spec:
  containers:
  - name: <container-name>
    resources:
      limits:
        memory: "1Gi"  # Increase as needed
      requests:
        memory: "512Mi"

2. Add memory monitoring:
spec:
  containers:
  - name: <container-name>
    env:
    - name: JAVA_OPTS  # For Java apps
      value: "-Xmx800m -XX:+UseG1GC"
"""
    
    def _generate_scheduling_yaml_patch(self, pod_data: Dict[str, Any]) -> str:
        """Generate YAML patch for scheduling issues"""
        return """
# Fixes for pod scheduling issues:

1. Reduce resource requests:
spec:
  containers:
  - name: <container-name>
    resources:
      requests:
        memory: "128Mi"  # Reduce if too high
        cpu: "100m"

2. Add node selector (if needed):
spec:
  nodeSelector:
    kubernetes.io/os: linux

3. Add tolerations (if needed):
spec:
  tolerations:
  - key: "node-role.kubernetes.io/master"
    operator: "Exists"
    effect: "NoSchedule"
"""
    
    def _generate_summary(self, recommendations: Dict[str, Any]) -> str:
        """Generate a summary of the recommendations"""
        issue_count = len(recommendations.get("issues_analyzed", []))
        command_count = len(recommendations.get("commands", []))
        
        return f"Found {issue_count} issues with {command_count} recommended diagnostic commands and specific fixes provided."
    
    def _calculate_confidence_score(self, recommendations: Dict[str, Any]) -> float:
        """Calculate confidence score for the recommendations"""
        # Simple scoring based on number of specific recommendations
        issues = len(recommendations.get("issues_analyzed", []))
        commands = len(recommendations.get("commands", []))
        fixes = len(recommendations.get("quick_fixes", []))
        
        if issues == 0:
            return 0.0
        
        # Base score on coverage
        score = min(1.0, (commands + fixes) / (issues * 3))
        return round(score, 2)
    
    def _initialize_issue_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known issue patterns and their characteristics"""
        return {
            "crashloopbackoff": {
                "keywords": ["crashloopbackoff", "crash loop"],
                "severity": "high",
                "category": "runtime"
            },
            "imagepull": {
                "keywords": ["imagepullbackoff", "errimagepull", "image pull"],
                "severity": "high", 
                "category": "configuration"
            },
            "oom": {
                "keywords": ["oomkilled", "out of memory", "memory"],
                "severity": "high",
                "category": "resources"
            },
            "pending": {
                "keywords": ["pending", "scheduling"],
                "severity": "medium",
                "category": "scheduling"
            }
        }
    
    def _initialize_fix_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize fix templates for common issues"""
        return {
            "memory_increase": {
                "description": "Increase memory limits",
                "yaml_patch": "resources.limits.memory",
                "commands": ["kubectl patch"]
            },
            "probe_adjustment": {
                "description": "Adjust health check probes", 
                "yaml_patch": "livenessProbe,readinessProbe",
                "commands": ["kubectl edit"]
            }
        }
