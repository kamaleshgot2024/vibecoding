"""
CLI Commands for KubeGPT
"""

import click
import json
import yaml
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from kubernetes.kubernetes_client import KubernetesClient
from ai.gpt_analyzer import GPTAnalyzer
from utils.config import Config
from utils.logger import setup_logger

console = Console()
logger = setup_logger()

@click.group()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--namespace', '-n', default=None, help='Kubernetes namespace')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, namespace, output, verbose):
    """KubeGPT - Kubernetes Pod Diagnostics CLI Tool"""
    ctx.ensure_object(dict)
    
    # Load configuration
    try:
        ctx.obj['config'] = Config(config)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        ctx.exit(1)
    
    # Set namespace
    ctx.obj['namespace'] = namespace or ctx.obj['config'].get('kubernetes.default_namespace', 'default')
    ctx.obj['output'] = output
    ctx.obj['verbose'] = verbose
    
    # Initialize Kubernetes client
    try:
        ctx.obj['k8s_client'] = KubernetesClient(ctx.obj['config'])
    except Exception as e:
        console.print(f"[red]Error connecting to Kubernetes: {e}[/red]")
        ctx.exit(1)


@cli.command()
@click.option('--pod-name', '-p', help='Pod name to analyze')
@click.option('--container', help='Specific container name in the pod')
@click.option('--use-ai', is_flag=True, help='Use AI for intelligent analysis')
@click.pass_context
def analyze(ctx, pod_name, container, use_ai):
    """Analyze pod health and diagnose issues"""
    k8s_client = ctx.obj['k8s_client']
    namespace = ctx.obj['namespace']
    output_format = ctx.obj['output']
    
    try:
        if pod_name:
            # Analyze specific pod
            pod_info = k8s_client.get_pod_info(pod_name, namespace)
            pod_logs = k8s_client.get_pod_logs(pod_name, namespace, container)
            pod_events = k8s_client.get_pod_events(pod_name, namespace)
            
            analysis_data = {
                'pod_info': pod_info,
                'logs': pod_logs,
                'events': pod_events
            }
            
            if use_ai:
                gpt_analyzer = GPTAnalyzer(ctx.obj['config'])
                ai_analysis = gpt_analyzer.analyze_pod_issues(analysis_data)
                analysis_data['ai_analysis'] = ai_analysis
            
            _display_analysis(analysis_data, output_format, pod_name)
        else:
            # Analyze all pods in namespace
            pods = k8s_client.list_pods(namespace)
            
            if output_format == 'table':
                _display_pods_table(pods)
            else:
                _display_output(pods, output_format)
                
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        logger.error(f"Analysis error: {e}")


@cli.command()
@click.option('--pod-name', '-p', required=True, help='Pod name')
@click.option('--container', help='Container name')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--tail', type=int, default=100, help='Number of lines to show from the end of the logs')
@click.pass_context
def logs(ctx, pod_name, container, follow, tail):
    """Get and analyze pod logs"""
    k8s_client = ctx.obj['k8s_client']
    namespace = ctx.obj['namespace']
    output_format = ctx.obj['output']
    
    try:
        if follow:
            console.print(f"[green]Following logs for pod {pod_name}...[/green]")
            k8s_client.follow_pod_logs(pod_name, namespace, container)
        else:
            logs_data = k8s_client.get_pod_logs(pod_name, namespace, container, tail=tail)
            
            if output_format == 'table':
                _display_logs_formatted(logs_data, pod_name)
            else:
                _display_output(logs_data, output_format)
                
    except Exception as e:
        console.print(f"[red]Error getting logs: {e}[/red]")
        logger.error(f"Logs error: {e}")


@cli.command()
@click.option('--pod-name', '-p', help='Pod name to get events for')
@click.pass_context
def events(ctx, pod_name):
    """Get and display Kubernetes events"""
    k8s_client = ctx.obj['k8s_client']
    namespace = ctx.obj['namespace']
    output_format = ctx.obj['output']
    
    try:
        if pod_name:
            events_data = k8s_client.get_pod_events(pod_name, namespace)
        else:
            events_data = k8s_client.get_namespace_events(namespace)
        
        if output_format == 'table':
            _display_events_table(events_data)
        else:
            _display_output(events_data, output_format)
            
    except Exception as e:
        console.print(f"[red]Error getting events: {e}[/red]")
        logger.error(f"Events error: {e}")


@cli.command()
@click.pass_context
def health_check(ctx):
    """Perform comprehensive health check of all pods in namespace"""
    k8s_client = ctx.obj['k8s_client']
    namespace = ctx.obj['namespace']
    output_format = ctx.obj['output']
    
    try:
        health_data = k8s_client.get_namespace_health(namespace)
        
        if output_format == 'table':
            _display_health_table(health_data)
        else:
            _display_output(health_data, output_format)
            
    except Exception as e:
        console.print(f"[red]Error during health check: {e}[/red]")
        logger.error(f"Health check error: {e}")


def _display_analysis(data, output_format, pod_name):
    """Display pod analysis results"""
    if output_format == 'table':
        console.print(Panel(f"[bold green]Analysis for Pod: {pod_name}[/bold green]"))
        
        # Pod Info
        pod_info = data['pod_info']
        info_table = Table(title="Pod Information")
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Name", pod_info.get('name', 'N/A'))
        info_table.add_row("Namespace", pod_info.get('namespace', 'N/A'))
        info_table.add_row("Status", pod_info.get('status', 'N/A'))
        info_table.add_row("Node", pod_info.get('node', 'N/A'))
        info_table.add_row("Created", pod_info.get('created', 'N/A'))
        
        console.print(info_table)
        
        # AI Analysis if available
        if 'ai_analysis' in data:
            console.print("\n")
            console.print(Panel(data['ai_analysis'], title="[bold blue]AI Analysis[/bold blue]"))
    else:
        _display_output(data, output_format)


def _display_pods_table(pods):
    """Display pods in table format"""
    table = Table(title="Pods Overview")
    table.add_column("Name", style="cyan")
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
    
    console.print(table)


def _display_logs_formatted(logs, pod_name):
    """Display logs in formatted way"""
    console.print(Panel(f"[bold green]Logs for Pod: {pod_name}[/bold green]"))
    
    for line in logs.split('\n'):
        if line.strip():
            # Color code log levels
            if 'ERROR' in line.upper() or 'FATAL' in line.upper():
                console.print(f"[red]{line}[/red]")
            elif 'WARN' in line.upper():
                console.print(f"[yellow]{line}[/yellow]")
            elif 'INFO' in line.upper():
                console.print(f"[blue]{line}[/blue]")
            else:
                console.print(line)


def _display_events_table(events):
    """Display events in table format"""
    table = Table(title="Kubernetes Events")
    table.add_column("Type", style="cyan")
    table.add_column("Reason", style="white")
    table.add_column("Object", style="green")
    table.add_column("Message", style="white")
    table.add_column("Age", style="blue")
    
    for event in events:
        type_color = "red" if event['type'] == "Warning" else "green"
        table.add_row(
            f"[{type_color}]{event['type']}[/{type_color}]",
            event['reason'],
            event['object'],
            event['message'][:50] + "..." if len(event['message']) > 50 else event['message'],
            event['age']
        )
    
    console.print(table)


def _display_health_table(health_data):
    """Display health check results"""
    console.print(Panel("[bold green]Namespace Health Check[/bold green]"))
    
    # Summary
    summary_table = Table(title="Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("Total Pods", str(health_data['total_pods']))
    summary_table.add_row("Running Pods", f"[green]{health_data['running_pods']}[/green]")
    summary_table.add_row("Failed Pods", f"[red]{health_data['failed_pods']}[/red]")
    summary_table.add_row("Pending Pods", f"[yellow]{health_data['pending_pods']}[/yellow]")
    
    console.print(summary_table)
    
    # Failed pods details
    if health_data['failed_pods'] > 0:
        console.print("\n")
        failed_table = Table(title="Failed Pods")
        failed_table.add_column("Name", style="red")
        failed_table.add_column("Status", style="white")
        failed_table.add_column("Reason", style="yellow")
        
        for pod in health_data['failed_pod_details']:
            failed_table.add_row(pod['name'], pod['status'], pod['reason'])
        
        console.print(failed_table)


def _display_output(data, output_format):
    """Display data in specified format"""
    if output_format == 'json':
        console.print(json.dumps(data, indent=2, default=str))
    elif output_format == 'yaml':
        console.print(yaml.dump(data, default_flow_style=False))
    else:
        console.print(str(data))
