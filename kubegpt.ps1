# KubeGPT PowerShell Script
# Provides easy access to KubeGPT commands on Windows

param(
    [string]$Command = "",
    [string]$PodName = "",
    [string]$Namespace = "default",
    [switch]$UseAI,
    [switch]$Help
)

# Set script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to display help
function Show-Help {
    Write-Host "KubeGPT PowerShell Wrapper" -ForegroundColor Green
    Write-Host "Usage: .\kubegpt.ps1 [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Cyan
    Write-Host "  -Command     : KubeGPT command to run (analyze, logs, events, health-check)"
    Write-Host "  -PodName     : Name of the pod to analyze"
    Write-Host "  -Namespace   : Kubernetes namespace (default: 'default')"
    Write-Host "  -UseAI       : Enable AI-powered analysis"
    Write-Host "  -Help        : Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\kubegpt.ps1 -Command analyze -Namespace kube-system"
    Write-Host "  .\kubegpt.ps1 -Command analyze -PodName nginx-pod -UseAI"
    Write-Host "  .\kubegpt.ps1 -Command logs -PodName nginx-pod"
    Write-Host "  .\kubegpt.ps1 -Command health-check"
    Write-Host ""
    Write-Host "Interactive mode:" -ForegroundColor Yellow
    Write-Host "  .\kubegpt.ps1"
    Write-Host ""
}

# Function to run KubeGPT command
function Invoke-KubeGPT {
    param([string]$Args)
    
    try {
        Write-Host "Running: python kubegpt.py $Args" -ForegroundColor Cyan
        $result = python kubegpt.py $Args.Split(' ')
        return $result
    }
    catch {
        Write-Host "Error running KubeGPT: $_" -ForegroundColor Red
        return $null
    }
}

# Function for interactive menu
function Show-InteractiveMenu {
    while ($true) {
        Clear-Host
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "          KubeGPT - Main Menu          " -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "1. Analyze all pods in a namespace"
        Write-Host "2. Analyze specific pod"
        Write-Host "3. Get pod logs"
        Write-Host "4. Show pod events"
        Write-Host "5. Health check"
        Write-Host "6. Run custom command"
        Write-Host "7. Show help"
        Write-Host "8. Exit"
        Write-Host ""
        
        $choice = Read-Host "Please select an option (1-8)"
        
        switch ($choice) {
            "1" {
                $ns = Read-Host "Enter namespace (default: default)"
                if ([string]::IsNullOrEmpty($ns)) { $ns = "default" }
                Invoke-KubeGPT "analyze --namespace $ns"
                Read-Host "Press Enter to continue"
            }
            "2" {
                $pod = Read-Host "Enter pod name"
                $ns = Read-Host "Enter namespace (default: default)"
                if ([string]::IsNullOrEmpty($ns)) { $ns = "default" }
                $ai = Read-Host "Use AI analysis? (y/n)"
                
                $cmd = "analyze --pod-name $pod --namespace $ns"
                if ($ai -eq "y" -or $ai -eq "Y") {
                    $cmd += " --use-ai"
                }
                
                Invoke-KubeGPT $cmd
                Read-Host "Press Enter to continue"
            }
            "3" {
                $pod = Read-Host "Enter pod name"
                $ns = Read-Host "Enter namespace (default: default)"
                if ([string]::IsNullOrEmpty($ns)) { $ns = "default" }
                $tail = Read-Host "Number of log lines to show (default: 100)"
                if ([string]::IsNullOrEmpty($tail)) { $tail = "100" }
                
                Invoke-KubeGPT "logs --pod-name $pod --namespace $ns --tail $tail"
                Read-Host "Press Enter to continue"
            }
            "4" {
                $ns = Read-Host "Enter namespace (default: default)"
                if ([string]::IsNullOrEmpty($ns)) { $ns = "default" }
                
                Invoke-KubeGPT "events --namespace $ns"
                Read-Host "Press Enter to continue"
            }
            "5" {
                $ns = Read-Host "Enter namespace (default: default)"
                if ([string]::IsNullOrEmpty($ns)) { $ns = "default" }
                
                Invoke-KubeGPT "health-check --namespace $ns"
                Read-Host "Press Enter to continue"
            }
            "6" {
                $customCmd = Read-Host "Enter your custom KubeGPT command (without 'python kubegpt.py')"
                Invoke-KubeGPT $customCmd
                Read-Host "Press Enter to continue"
            }
            "7" {
                Show-Help
                Read-Host "Press Enter to continue"
            }
            "8" {
                Write-Host "Thank you for using KubeGPT!" -ForegroundColor Green
                return
            }
            default {
                Write-Host "Invalid option. Please try again." -ForegroundColor Red
                Start-Sleep 2
            }
        }
    }
}

# Main script logic
if ($Help) {
    Show-Help
    exit 0
}

# Check if Python is available
if (-not (Test-Command "python")) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    exit 1
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import click, kubernetes, rich" 2>$null
}
catch {
    Write-Host "Installing required dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Handle command line arguments
if ($Command) {
    $args = @("$Command")
    
    if ($PodName) {
        $args += "--pod-name", $PodName
    }
    
    if ($Namespace -ne "default") {
        $args += "--namespace", $Namespace
    }
    
    if ($UseAI) {
        $args += "--use-ai"
    }
    
    $argsString = $args -join " "
    Invoke-KubeGPT $argsString
}
else {
    # Interactive mode
    Show-InteractiveMenu
}
