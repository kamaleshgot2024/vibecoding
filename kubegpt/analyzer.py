"""
AI Analyzer Module

This module handles AI-powered analysis of Kubernetes pod issues.
Currently supports OpenAI GPT models, with placeholders for other AI services.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Optional AI dependencies
logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    import yaml
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI or YAML module not available")


class AIAnalyzer:
    """
    AI-powered analyzer for Kubernetes pod diagnostics
    
    This class integrates with various AI services (primarily OpenAI GPT)
    to provide intelligent analysis and recommendations for pod issues.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI analyzer
        
        Args:
            model: AI model to use for analysis
        """
        # Load API key from config.yaml
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
            self.api_key = config.get("openai", {}).get("api_key", None)

        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"AI analyzer initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("AI analysis not available - OpenAI not configured or dependencies missing")
    
    def analyze_pod_issues(self, pod_data: Dict[str, Any]) -> str:
        """
        Analyze pod issues using AI and provide comprehensive insights
        
        Args:
            pod_data: Complete pod information from diagnoser
            
        Returns:
            AI-generated analysis and recommendations
        """
        if not self.client:
            return self._fallback_analysis(pod_data)
        
        try:
            # Prepare comprehensive context for AI analysis
            analysis_context = self._prepare_analysis_context(pod_data)
            
            # Create AI prompt
            prompt = self._create_analysis_prompt(analysis_context)
            
            # Get AI analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            logger.info("AI analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"AI analysis failed: {e}\n\n{self._fallback_analysis(pod_data)}"
    
    def analyze_logs_for_errors(self, logs: str, pod_name: str) -> str:
        """
        Analyze pod logs specifically for error patterns and root causes
        
        Args:
            logs: Pod log content
            pod_name: Name of the pod
            
        Returns:
            AI-generated log analysis
        """
        if not self.client:
            return self._fallback_log_analysis(logs)
        
        try:
            prompt = f"""
            Analyze the following Kubernetes pod logs for '{pod_name}' and identify:
            
            1. **Error Patterns**: Any errors, exceptions, or warning messages
            2. **Root Causes**: Likely causes of the identified issues
            3. **Immediate Actions**: Specific steps to investigate further
            4. **kubectl Commands**: Useful commands to gather more information
            
            LOGS (last 2000 characters):
            ```
            {logs[-2000:]}
            ```
            
            Provide actionable insights with specific kubectl commands where applicable.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Kubernetes expert specializing in log analysis and troubleshooting. Provide specific, actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI log analysis failed: {e}")
            return self._fallback_log_analysis(logs)
    
    def suggest_yaml_fixes(self, pod_data: Dict[str, Any], issues: List[str]) -> str:
        """
        Generate YAML configuration fixes based on identified issues
        
        Args:
            pod_data: Pod information
            issues: List of identified issues
            
        Returns:
            AI-generated YAML fixes and explanations
        """
        if not self.client:
            return self._fallback_yaml_suggestions(issues)
        
        try:
            pod_spec = pod_data.get("pod_info", {}).get("spec", {})
            
            prompt = f"""
            Based on the following Kubernetes pod issues, suggest specific YAML fixes:
            
            **Pod Name**: {pod_data.get('name', 'Unknown')}
            **Issues Found**: {', '.join(issues)}
            
            **Current Pod Spec (relevant parts)**:
            ```yaml
            {json.dumps(pod_spec, indent=2)[:1000]}
            ```
            
            Provide:
            1. **Specific YAML patches** to address each issue
            2. **Explanations** for why each change helps
            3. **kubectl patch commands** to apply the fixes
            4. **Alternative approaches** if applicable
            
            Focus on practical, production-ready solutions.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Kubernetes YAML expert. Provide specific, production-ready YAML fixes with clear explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI YAML suggestion failed: {e}")
            return self._fallback_yaml_suggestions(issues)
    
    def get_troubleshooting_steps(self, issue_description: str, pod_context: Dict[str, Any]) -> str:
        """
        Get step-by-step troubleshooting guide for specific issues
        
        Args:
            issue_description: Description of the issue
            pod_context: Pod context information
            
        Returns:
            AI-generated troubleshooting steps
        """
        if not self.client:
            return self._fallback_troubleshooting_steps(issue_description)
        
        try:
            prompt = f"""
            Provide a step-by-step troubleshooting guide for this Kubernetes issue:
            
            **Issue**: {issue_description}
            **Pod**: {pod_context.get('name', 'Unknown')}
            **Namespace**: {pod_context.get('namespace', 'default')}
            **Current Status**: {pod_context.get('status', 'Unknown')}
            
            Structure your response as:
            
            ## 🔍 Initial Diagnosis
            [Immediate checks to perform]
            
            ## 📋 Step-by-Step Investigation
            [Numbered steps with specific kubectl commands]
            
            ## 🔧 Resolution Steps
            [Specific actions to resolve the issue]
            
            ## 🛡️ Prevention
            [How to prevent this issue in the future]
            
            Include specific kubectl commands, file paths, and configuration examples.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior Kubernetes administrator providing detailed troubleshooting guidance. Be specific and practical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI troubleshooting guide failed: {e}")
            return self._fallback_troubleshooting_steps(issue_description)
    
    def _prepare_analysis_context(self, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured context for AI analysis"""
        context = {
            "pod_name": pod_data.get("name", "Unknown"),
            "namespace": pod_data.get("namespace", "default"),
            "status": pod_data.get("status", "Unknown"),
            "issues": pod_data.get("issues", []),
            "timestamp": pod_data.get("timestamp", ""),
        }
        
        # Add pod status details
        pod_info = pod_data.get("pod_info", {})
        if pod_info:
            status = pod_info.get("status", {})
            context["phase"] = status.get("phase", "Unknown")
            context["conditions"] = status.get("conditions", [])
            context["container_statuses"] = status.get("containerStatuses", [])
        
        # Add recent logs (truncated)
        logs = pod_data.get("logs", "")
        context["recent_logs"] = logs[-1500:] if logs else "No logs available"
        
        # Add recent events
        events = pod_data.get("events", [])
        context["recent_events"] = events[:5] if events else []
        
        return context
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt for AI"""
        return f"""
        Analyze this Kubernetes pod and provide comprehensive diagnostics:
        
        **Pod Information:**
        - Name: {context['pod_name']}
        - Namespace: {context['namespace']}
        - Status: {context['status']} (Phase: {context.get('phase', 'Unknown')})
        - Detected Issues: {', '.join(context['issues']) if context['issues'] else 'None detected'}
        
        **Container Statuses:**
        {json.dumps(context.get('container_statuses', []), indent=2)[:500]}
        
        **Recent Logs:**
        ```
        {context['recent_logs']}
        ```
        
        **Recent Events:**
        {json.dumps(context.get('recent_events', []), indent=2)[:500]}
        
        Provide:
        
        ## 🔍 **Status Assessment**
        [Current health and state analysis]
        
        ## ⚠️ **Issues Identified**
        [Specific problems found with severity levels]
        
        ## 🎯 **Root Cause Analysis**
        [Likely causes of the issues]
        
        ## 🔧 **Immediate Actions**
        [Specific kubectl commands to run NOW]
        
        ## 📝 **Configuration Fixes**
        [YAML changes or kubectl patch commands]
        
        ## 🛡️ **Prevention & Best Practices**
        [How to prevent similar issues]
        
        Be specific, actionable, and include exact kubectl commands.
        """
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis"""
        return """
        You are KubeGPT, an expert Kubernetes troubleshooting assistant with deep knowledge of:
        - Pod lifecycle and common failure modes
        - Container runtime issues (Docker, containerd, CRI-O)
        - Resource management and limits
        - Networking and service discovery
        - Storage and persistent volumes
        - Security and RBAC
        - Cluster components and architecture
        
        Your responses should be:
        - **Precise**: Use exact kubectl commands and specific file paths
        - **Actionable**: Provide steps that can be executed immediately
        - **Educational**: Explain WHY something is happening
        - **Safe**: Warn about potentially destructive operations
        - **Structured**: Use clear headings and bullet points
        
        Always prioritize immediate remediation steps and include specific commands.
        Consider production environment constraints and safety.
        """
    
    def _fallback_analysis(self, pod_data: Dict[str, Any]) -> str:
        """Provide basic analysis when AI is not available"""
        issues = pod_data.get("issues", [])
        status = pod_data.get("status", "Unknown")
        
        analysis = f"""
        ## 📊 Basic Analysis (AI not available)
        
        **Pod Status**: {status}
        **Issues Found**: {len(issues)}
        
        """
        
        if issues:
            analysis += "**Detected Issues:**\n"
            for i, issue in enumerate(issues, 1):
                analysis += f"{i}. {issue}\n"
        
        analysis += """
        
        **Recommended Actions:**
        1. Check pod logs: `kubectl logs <pod-name> -n <namespace>`
        2. Describe pod: `kubectl describe pod <pod-name> -n <namespace>`
        3. Check events: `kubectl get events -n <namespace>`
        4. Verify resource limits and requests
        5. Check node resources: `kubectl describe node <node-name>`
        
        **Note**: For AI-powered analysis, configure OpenAI API key.
        """
        
        return analysis
    
    def _fallback_log_analysis(self, logs: str) -> str:
        """Provide basic log analysis when AI is not available"""
        error_patterns = ["error", "exception", "fatal", "panic", "failed"]
        
        analysis = "## 📝 Basic Log Analysis (AI not available)\n\n"
        
        for pattern in error_patterns:
            if pattern.lower() in logs.lower():
                analysis += f"- Found '{pattern}' patterns in logs\n"
        
        analysis += "\n**Recommended**: Configure OpenAI API key for detailed log analysis."
        
        return analysis
    
    def _fallback_yaml_suggestions(self, issues: List[str]) -> str:
        """Provide basic YAML suggestions when AI is not available"""
        suggestions = "## 📝 Basic YAML Suggestions (AI not available)\n\n"
        
        for issue in issues:
            if "memory" in issue.lower() or "oom" in issue.lower():
                suggestions += "- Consider increasing memory limits in pod spec\n"
            elif "cpu" in issue.lower():
                suggestions += "- Review CPU requests and limits\n"
            elif "image" in issue.lower():
                suggestions += "- Verify image name and registry access\n"
        
        suggestions += "\n**Recommended**: Configure OpenAI API key for detailed YAML fixes."
        
        return suggestions
    
    def _fallback_troubleshooting_steps(self, issue: str) -> str:
        """Provide basic troubleshooting steps when AI is not available"""
        return f"""
        ## 🔍 Basic Troubleshooting Steps (AI not available)
        
        **Issue**: {issue}
        
        **General Steps:**
        1. `kubectl describe pod <pod-name> -n <namespace>`
        2. `kubectl logs <pod-name> -n <namespace>`
        3. `kubectl get events -n <namespace>`
        4. `kubectl get pod <pod-name> -o yaml`
        
        **Recommended**: Configure OpenAI API key for detailed troubleshooting guidance.
        """
