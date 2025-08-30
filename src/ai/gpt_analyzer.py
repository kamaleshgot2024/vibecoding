"""
GPT Analyzer for KubeGPT

Uses OpenAI GPT models to provide intelligent analysis of Kubernetes pod issues.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTAnalyzer:
    """AI-powered analyzer for Kubernetes pod diagnostics"""
    
    def __init__(self, config):
        """Initialize GPT analyzer with configuration"""
        self.config = config
        self.api_key = self._get_api_key()
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.model = config.get('openai.model', 'gpt-3.5-turbo')
            self.max_tokens = config.get('openai.max_tokens', 1000)
            self.temperature = config.get('openai.temperature', 0.3)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. AI analysis will be disabled.")
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment"""
        # First try config
        api_key = self.config.get('openai.api_key')
        if api_key and api_key.startswith('${') and api_key.endswith('}'):
            # Environment variable reference
            env_var = api_key[2:-1]
            api_key = os.getenv(env_var)
        
        # Fallback to environment
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        return api_key
    
    def analyze_pod_issues(self, pod_data: Dict[str, Any]) -> str:
        """Analyze pod issues using GPT and provide recommendations"""
        if not self.client:
            return "AI analysis is not available. Please configure OpenAI API key."
        
        try:
            # Prepare the analysis prompt
            prompt = self._create_analysis_prompt(pod_data)
            
            # Call OpenAI API
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
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            analysis = response.choices[0].message.content
            return analysis
            
        except Exception as e:
            logger.error(f"Error during AI analysis: {e}")
            return f"AI analysis failed: {e}"
    
    def analyze_logs(self, logs: str, pod_name: str) -> str:
        """Analyze pod logs specifically"""
        if not self.client:
            return "AI log analysis is not available. Please configure OpenAI API key."
        
        try:
            prompt = f"""
            Please analyze the following logs from Kubernetes pod '{pod_name}' and identify any issues or errors:
            
            LOGS:
            {logs[:3000]}  # Limit log size
            
            Please provide:
            1. Summary of any errors or warnings found
            2. Potential root causes
            3. Recommended solutions
            4. Any patterns or recurring issues
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Kubernetes expert specializing in log analysis and troubleshooting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error during log analysis: {e}")
            return f"Log analysis failed: {e}"
    
    def analyze_events(self, events: list, context: str = "") -> str:
        """Analyze Kubernetes events"""
        if not self.client:
            return "AI event analysis is not available. Please configure OpenAI API key."
        
        try:
            events_text = json.dumps(events[:10], indent=2)  # Limit to recent 10 events
            
            prompt = f"""
            Please analyze the following Kubernetes events{' for ' + context if context else ''}:
            
            EVENTS:
            {events_text}
            
            Please provide:
            1. Summary of significant events
            2. Any warning or error events that need attention
            3. Potential issues or patterns
            4. Recommended actions
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Kubernetes expert specializing in event analysis and cluster troubleshooting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error during event analysis: {e}")
            return f"Event analysis failed: {e}"
    
    def get_troubleshooting_steps(self, issue_description: str) -> str:
        """Get troubleshooting steps for a specific issue"""
        if not self.client:
            return "AI troubleshooting is not available. Please configure OpenAI API key."
        
        try:
            prompt = f"""
            I'm experiencing the following Kubernetes issue:
            {issue_description}
            
            Please provide detailed troubleshooting steps including:
            1. Initial diagnostic commands to run
            2. Common causes and how to check for them
            3. Step-by-step resolution process
            4. Prevention strategies
            5. Relevant kubectl commands with examples
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_troubleshooting_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting troubleshooting steps: {e}")
            return f"Troubleshooting analysis failed: {e}"
    
    def _create_analysis_prompt(self, pod_data: Dict[str, Any]) -> str:
        """Create a comprehensive analysis prompt"""
        pod_info = pod_data.get('pod_info', {})
        logs = pod_data.get('logs', '')[:2000]  # Limit log size
        events = pod_data.get('events', [])[:5]  # Limit to recent 5 events
        
        prompt = f"""
        Please analyze the following Kubernetes pod data and provide a comprehensive diagnostic report:

        POD INFORMATION:
        - Name: {pod_info.get('name', 'Unknown')}
        - Namespace: {pod_info.get('namespace', 'Unknown')}
        - Status: {pod_info.get('status', 'Unknown')}
        - Node: {pod_info.get('node', 'Unknown')}
        - Age: {pod_info.get('age', 'Unknown')}
        - Containers: {json.dumps(pod_info.get('containers', []), indent=2)}
        - Conditions: {json.dumps(pod_info.get('conditions', []), indent=2)}

        RECENT LOGS:
        {logs}

        RECENT EVENTS:
        {json.dumps(events, indent=2)}

        Please provide:
        1. **Status Assessment**: Current health status of the pod
        2. **Issue Identification**: Any problems, errors, or anomalies detected
        3. **Root Cause Analysis**: Likely causes of any identified issues
        4. **Recommendations**: Specific actions to resolve problems
        5. **Prevention**: How to prevent similar issues in the future
        6. **Monitoring**: What to monitor going forward
        
        Please be specific and actionable in your recommendations.
        """
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for general pod analysis"""
        return """
        You are KubeGPT, an expert Kubernetes troubleshooting assistant. You specialize in:
        - Diagnosing pod failures and issues
        - Analyzing logs and events
        - Providing actionable troubleshooting steps
        - Recommending best practices
        - Explaining complex Kubernetes concepts clearly
        
        Your responses should be:
        - Clear and concise
        - Technically accurate
        - Actionable with specific commands when helpful
        - Focused on practical solutions
        - Structured with clear sections
        
        Always consider the context of production environments and provide safe, tested recommendations.
        """
    
    def _get_troubleshooting_system_prompt(self) -> str:
        """Get system prompt for troubleshooting guidance"""
        return """
        You are a senior Kubernetes administrator and troubleshooting expert. Your role is to provide:
        - Step-by-step troubleshooting procedures
        - Relevant kubectl commands with proper syntax
        - Common pitfalls and how to avoid them
        - Best practices for resolution
        - Clear explanations of what each step accomplishes
        
        Structure your responses with:
        1. Immediate diagnostic steps
        2. Progressive troubleshooting approach
        3. Specific commands to run
        4. Expected outputs and what they mean
        5. Resolution steps
        6. Verification procedures
        
        Always prioritize safe operations and include warnings for potentially disruptive commands.
        """
