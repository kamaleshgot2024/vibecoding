"""
CLI entry point for KubeGPT

This module provides the main command-line interface using Typer.
It orchestrates pod diagnosis, analysis, and recommendations.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from .diagnoser import PodDiagnoser
from .analyzer import AIAnalyzer
from .recommender import FixRecommender

# Initialize console for rich output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="kubegpt",
    help="🤖 AI-powered Kubernetes pod diagnostics tool",
    add_completion=False,
    rich_markup_mode="rich"
)

@app.command()
def diagnose(
    pod_name: str = typer.Argument(..., help="Name of the pod to diagnose"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    use_ai: bool = typer.Option(False, "--ai", help="Use AI for intelligent analysis"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, json, yaml"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
) -> None:
    """
    🔍 Diagnose issues with a specific Kubernetes pod
    
    This command will:
    1. Gather pod information using kubectl
    2. Analyze common issues (CrashLoopBackOff, OOMKilled, etc.)
    3. Provide AI-powered insights (if enabled)
    4. Suggest actionable kubectl commands and YAML fixes
    """
    console.print(Panel(f"🔍 Diagnosing pod: [bold green]{pod_name}[/bold green] in namespace: [bold blue]{namespace}[/bold blue]"))
    
    try:
        # Step 1: Gather pod information
        diagnoser = PodDiagnoser(namespace=namespace, verbose=verbose)
        pod_data = diagnoser.diagnose_pod(pod_name)
        
        if not pod_data:
            console.print("[red]❌ Failed to gather pod information[/red]")
            raise typer.Exit(1)
        
        # Step 2: Generate recommendations based on common patterns
        recommender = FixRecommender()
        recommendations = recommender.analyze_and_recommend(pod_data)
        
        # Step 3: AI analysis (if enabled)
        ai_insights = None
        if use_ai:
            console.print("🤖 Running AI analysis...")
            analyzer = AIAnalyzer()
            ai_insights = analyzer.analyze_pod_issues(pod_data)
        
        # Step 4: Display results
        _display_diagnosis_results(pod_data, recommendations, ai_insights, output_format)
        
    except Exception as e:
        console.print(f"[red]❌ Error during diagnosis: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def scan(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace to scan"),
    all_namespaces: bool = typer.Option(False, "--all", "-A", help="Scan all namespaces"),
    problematic_only: bool = typer.Option(True, "--problems-only", "-p", help="Show only problematic pods"),
    use_ai: bool = typer.Option(False, "--ai", help="Use AI for analysis of problematic pods")
) -> None:
    """
    🔍 Scan namespace(s) for problematic pods
    
    Identifies pods with common issues and provides quick recommendations.
    """
    target = "all namespaces" if all_namespaces else f"namespace: {namespace}"
    console.print(Panel(f"🔍 Scanning {target} for problematic pods"))
    
    try:
        diagnoser = PodDiagnoser(namespace=None if all_namespaces else namespace)
        problematic_pods = diagnoser.scan_for_problems(all_namespaces)
        
        if not problematic_pods:
            console.print("[green]✅ No problematic pods found![/green]")
            return
        
        recommender = FixRecommender()
        
        for pod_info in problematic_pods:
            _display_pod_summary(pod_info, recommender, use_ai)
            
    except Exception as e:
        console.print(f"[red]❌ Error during scan: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def logs(
    pod_name: str = typer.Argument(..., help="Name of the pod"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    container: Optional[str] = typer.Option(None, "--container", "-c", help="Specific container name"),
    tail: int = typer.Option(100, "--tail", "-t", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    analyze: bool = typer.Option(True, "--analyze", help="Analyze logs for errors")
) -> None:
    """
    📝 Get and analyze pod logs
    
    Retrieves pod logs and optionally analyzes them for common error patterns.
    """
    console.print(Panel(f"📝 Getting logs for pod: [bold green]{pod_name}[/bold green]"))
    
    try:
        diagnoser = PodDiagnoser(namespace=namespace)
        
        if follow:
            diagnoser.follow_logs(pod_name, container)
        else:
            logs = diagnoser.get_pod_logs(pod_name, container, tail)
            
            if analyze:
                recommender = FixRecommender()
                log_analysis = recommender.analyze_logs(logs)
                console.print(Panel(log_analysis, title="📊 Log Analysis"))
            
            console.print(Panel(logs, title=f"📝 Logs ({tail} lines)"))
            
    except Exception as e:
        console.print(f"[red]❌ Error getting logs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def events(
    pod_name: Optional[str] = typer.Argument(None, help="Pod name (optional, shows all events if not specified)"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    recent: int = typer.Option(20, "--recent", "-r", help="Number of recent events to show")
) -> None:
    """
    📅 Get Kubernetes events for troubleshooting
    
    Shows recent events that might help diagnose pod issues.
    """
    target = f"pod: {pod_name}" if pod_name else f"namespace: {namespace}"
    console.print(Panel(f"📅 Getting events for {target}"))
    
    try:
        diagnoser = PodDiagnoser(namespace=namespace)
        events = diagnoser.get_events(pod_name, recent)
        
        if not events:
            console.print("[yellow]⚠️ No recent events found[/yellow]")
            return
        
        _display_events(events)
        
    except Exception as e:
        console.print(f"[red]❌ Error getting events: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def fix(
    pod_name: str = typer.Argument(..., help="Name of the pod to generate fixes for"),
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    interactive: bool = typer.Option(True, "--interactive", "-i", help="Interactive mode for applying fixes"),
    dry_run: bool = typer.Option(True, "--dry-run", help="Show commands without executing them")
) -> None:
    """
    🔧 Generate and optionally apply fixes for pod issues
    
    Analyzes pod problems and provides actionable kubectl commands and YAML suggestions.
    """
    console.print(Panel(f"🔧 Generating fixes for pod: [bold green]{pod_name}[/bold green]"))
    
    try:
        # Diagnose the pod first
        diagnoser = PodDiagnoser(namespace=namespace)
        pod_data = diagnoser.diagnose_pod(pod_name)
        
        if not pod_data:
            console.print("[red]❌ Could not gather pod information[/red]")
            raise typer.Exit(1)
        
        # Generate recommendations
        recommender = FixRecommender()
        recommendations = recommender.generate_fixes(pod_data)
        
        _display_fix_recommendations(recommendations, interactive, dry_run)
        
    except Exception as e:
        console.print(f"[red]❌ Error generating fixes: {e}[/red]")
        raise typer.Exit(1)


def _display_diagnosis_results(pod_data: dict, recommendations: dict, ai_insights: Optional[str], output_format: str) -> None:
    """Display comprehensive diagnosis results"""
    if output_format == "json":
        import json
        result = {
            "pod_data": pod_data,
            "recommendations": recommendations,
            "ai_insights": ai_insights
        }
        console.print(json.dumps(result, indent=2, default=str))
        return
    
    # Rich format display
    console.print(Panel(f"📊 Pod Status: [bold]{pod_data.get('status', 'Unknown')}[/bold]"))
    
    if pod_data.get('issues'):
        console.print(Panel("\n".join([f"❌ {issue}" for issue in pod_data['issues']]), title="🚨 Issues Found"))
    
    if recommendations.get('commands'):
        console.print(Panel("\n".join(recommendations['commands']), title="🔧 Recommended Commands"))
    
    if recommendations.get('yaml_suggestions'):
        console.print(Panel(recommendations['yaml_suggestions'], title="📝 YAML Suggestions"))
    
    if ai_insights:
        console.print(Panel(ai_insights, title="🤖 AI Analysis"))


def _display_pod_summary(pod_info: dict, recommender, use_ai: bool) -> None:
    """Display summary of a problematic pod"""
    pod_name = pod_info.get('name', 'Unknown')
    status = pod_info.get('status', 'Unknown')
    issues = pod_info.get('issues', [])
    
    console.print(f"\n🔍 [bold red]{pod_name}[/bold red] - Status: [bold]{status}[/bold]")
    
    for issue in issues:
        console.print(f"  ❌ {issue}")
    
    # Quick recommendations
    quick_fixes = recommender.get_quick_fixes(pod_info)
    if quick_fixes:
        console.print("  🔧 Quick fixes:")
        for fix in quick_fixes:
            console.print(f"    • {fix}")


def _display_events(events: list) -> None:
    """Display Kubernetes events in a formatted way"""
    from rich.table import Table
    
    table = Table(title="📅 Recent Events")
    table.add_column("Type", style="cyan")
    table.add_column("Reason", style="white")
    table.add_column("Object", style="green")
    table.add_column("Message", style="white")
    table.add_column("Age", style="blue")
    
    for event in events:
        event_type = event.get('type', 'Unknown')
        type_color = "red" if event_type == "Warning" else "green"
        
        table.add_row(
            f"[{type_color}]{event_type}[/{type_color}]",
            event.get('reason', ''),
            event.get('object', ''),
            event.get('message', '')[:60] + "..." if len(event.get('message', '')) > 60 else event.get('message', ''),
            event.get('age', '')
        )
    
    console.print(table)


def _display_fix_recommendations(recommendations: dict, interactive: bool, dry_run: bool) -> None:
    """Display fix recommendations and optionally apply them"""
    if not recommendations:
        console.print("[yellow]⚠️ No specific fixes recommended[/yellow]")
        return
    
    commands = recommendations.get('commands', [])
    yaml_patches = recommendations.get('yaml_patches', [])
    
    if commands:
        console.print(Panel("\n".join(commands), title="🔧 Recommended kubectl Commands"))
        
        if interactive and not dry_run:
            for cmd in commands:
                if typer.confirm(f"Execute: {cmd}?"):
                    # Here you would execute the command
                    console.print(f"[green]✅ Would execute: {cmd}[/green]")
    
    if yaml_patches:
        console.print(Panel(yaml_patches, title="📝 YAML Patches"))


def main():
    """Entry point for the CLI application"""
    app()


if __name__ == "__main__":
    main()
