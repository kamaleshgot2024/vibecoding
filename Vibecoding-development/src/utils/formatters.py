"""
Output formatting utilities for KubeGPT
"""

import json
import yaml
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

console = Console()


class OutputFormatter:
    """Handles different output formats for KubeGPT"""
    
    @staticmethod
    def format_output(data: Any, output_format: str = 'table') -> str:
        """Format data according to specified format"""
        if output_format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif output_format == 'yaml':
            return yaml.dump(data, default_flow_style=False)
        else:
            return str(data)
    
    @staticmethod
    def print_json(data: Any):
        """Print data as formatted JSON"""
        json_str = json.dumps(data, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    @staticmethod
    def print_yaml(data: Any):
        """Print data as formatted YAML"""
        yaml_str = yaml.dump(data, default_flow_style=False)
        syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    @staticmethod
    def create_pods_table(pods: List[Dict[str, Any]]) -> Table:
        """Create a formatted table for pods"""
        table = Table(title="Kubernetes Pods")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Ready", style="green")
        table.add_column("Restarts", style="yellow")
        table.add_column("Age", style="white")
        table.add_column("Node", style="blue")
        
        for pod in pods:
            status_color = "green" if pod['status'] == "Running" else "red"
            table.add_row(
                pod['name'],
                f"[{status_color}]{pod['status']}[/{status_color}]",
                pod['ready'],
                str(pod['restarts']),
                pod['age'],
                pod['node']
            )
        
        return table
    
    @staticmethod
    def create_events_table(events: List[Dict[str, Any]]) -> Table:
        """Create a formatted table for events"""
        table = Table(title="Kubernetes Events")
        table.add_column("Type", style="cyan")
        table.add_column("Reason", style="white")
        table.add_column("Object", style="green")
        table.add_column("Message", style="white")
        table.add_column("Age", style="blue")
        
        for event in events:
            type_color = "red" if event['type'] == "Warning" else "green"
            message = event['message']
            if len(message) > 50:
                message = message[:47] + "..."
            
            table.add_row(
                f"[{type_color}]{event['type']}[/{type_color}]",
                event['reason'],
                event['object'],
                message,
                event['age']
            )
        
        return table
    
    @staticmethod
    def create_health_summary(health_data: Dict[str, Any]) -> Panel:
        """Create a health summary panel"""
        content = f"""
[bold]Namespace:[/bold] {health_data['namespace']}
[bold]Total Pods:[/bold] {health_data['total_pods']}
[bold green]Running:[/bold green] {health_data['running_pods']}
[bold red]Failed:[/bold red] {health_data['failed_pods']}
[bold yellow]Pending:[/bold yellow] {health_data['pending_pods']}
[bold]Health Score:[/bold] {health_data['health_score']:.1f}%
        """
        
        return Panel(content.strip(), title="[bold green]Namespace Health Summary[/bold green]")
    
    @staticmethod
    def format_logs(logs: str, pod_name: str) -> None:
        """Format and display logs with syntax highlighting"""
        console.print(Panel(f"[bold green]Logs for Pod: {pod_name}[/bold green]"))
        
        for line in logs.split('\n'):
            if line.strip():
                # Color code log levels
                if any(level in line.upper() for level in ['ERROR', 'FATAL', 'EXCEPTION']):
                    console.print(f"[red]{line}[/red]")
                elif any(level in line.upper() for level in ['WARN', 'WARNING']):
                    console.print(f"[yellow]{line}[/yellow]")
                elif any(level in line.upper() for level in ['INFO', 'INFORMATION']):
                    console.print(f"[blue]{line}[/blue]")
                elif 'DEBUG' in line.upper():
                    console.print(f"[dim]{line}[/dim]")
                else:
                    console.print(line)
    
    @staticmethod
    def format_analysis_result(analysis: str, title: str = "Analysis") -> Panel:
        """Format analysis result in a panel"""
        return Panel(analysis, title=f"[bold blue]{title}[/bold blue]", border_style="blue")
    
    @staticmethod
    def format_error(error_message: str) -> Panel:
        """Format error message"""
        return Panel(f"[red]{error_message}[/red]", title="[bold red]Error[/bold red]", border_style="red")
    
    @staticmethod
    def format_warning(warning_message: str) -> Panel:
        """Format warning message"""
        return Panel(f"[yellow]{warning_message}[/yellow]", title="[bold yellow]Warning[/bold yellow]", border_style="yellow")
    
    @staticmethod
    def format_success(success_message: str) -> Panel:
        """Format success message"""
        return Panel(f"[green]{success_message}[/green]", title="[bold green]Success[/bold green]", border_style="green")
