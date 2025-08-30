#!/usr/bin/env python3
"""
KubeGPT Quick Start Script

This script helps you get started with KubeGPT quickly by checking prerequisites
and running basic tests.
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Print the KubeGPT banner"""
    print("🚀" + "="*70 + "🚀")
    print("   KubeGPT - AI-Powered Kubernetes Diagnostics")
    print("   Quick Start & Environment Verification")
    print("🚀" + "="*70 + "🚀")

def check_python():
    """Check Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = ['typer', 'rich', 'openai', 'yaml', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"   ✅ {package} - installed")
        except ImportError:
            print(f"   ❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("   ✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_kubectl():
    """Check if kubectl is available and working"""
    print("\n⚙️ Checking kubectl...")
    
    try:
        # Check if kubectl is installed
        result = subprocess.run(['kubectl', 'version', '--client'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ kubectl - installed")
        else:
            print("   ❌ kubectl - not found")
            return False
        
        # Check cluster connection
        result = subprocess.run(['kubectl', 'cluster-info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Kubernetes cluster - connected")
            return True
        else:
            print("   ⚠️ Kubernetes cluster - not connected")
            print("   💡 You can still use KubeGPT in demo mode")
            return True
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ kubectl - not found or not responding")
        print("   💡 Install kubectl: https://kubernetes.io/docs/tasks/tools/")
        return False

def check_openai_key():
    """Check if OpenAI API key is configured"""
    print("\n🤖 Checking AI configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        if api_key.startswith('sk-') and len(api_key) > 20:
            print("   ✅ OpenAI API key - configured")
            return True
        else:
            print("   ⚠️ OpenAI API key - invalid format")
            return False
    else:
        print("   ⚠️ OpenAI API key - not configured")
        print("   💡 Set OPENAI_API_KEY environment variable for AI features")
        return False

def run_basic_test():
    """Run basic KubeGPT functionality test"""
    print("\n🧪 Running basic functionality test...")
    
    try:
        # Test help command
        result = subprocess.run([sys.executable, 'kubegpt.py', '--help'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("   ✅ KubeGPT CLI - working")
            return True
        else:
            print(f"   ❌ KubeGPT CLI - error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ KubeGPT CLI - timeout")
        return False
    except Exception as e:
        print(f"   ❌ KubeGPT CLI - error: {e}")
        return False

def suggest_next_steps():
    """Suggest what to do next"""
    print("\n🎯 Quick Start Commands:")
    print("   🔍 Basic scan:        python kubegpt.py scan")
    print("   🧪 Diagnose pod:     python kubegpt.py diagnose <pod-name>")
    print("   🤖 With AI:          python kubegpt.py diagnose <pod-name> --ai")
    print("   📚 Get help:         python kubegpt.py --help")
    print("   🎮 Try demo:         python innovation_demo.py")
    print("   📖 Full guide:       See HOW_TO_RUN.md")

def main():
    """Main function"""
    print_banner()
    
    # Check all prerequisites
    all_good = True
    
    if not check_python():
        all_good = False
    
    if not check_dependencies():
        all_good = False
    
    kubectl_ok = check_kubectl()
    ai_ok = check_openai_key()
    
    if not run_basic_test():
        all_good = False
    
    # Summary
    print("\n" + "="*70)
    if all_good:
        print("🎉 SUCCESS! KubeGPT is ready to use!")
    else:
        print("⚠️ SETUP INCOMPLETE - Please fix the issues above")
    
    if kubectl_ok:
        print("✅ Kubernetes integration ready")
    else:
        print("⚠️ Kubernetes integration needs setup")
    
    if ai_ok:
        print("✅ AI features ready")
    else:
        print("⚠️ AI features need OpenAI API key")
    
    suggest_next_steps()
    print("="*70)

if __name__ == "__main__":
    main()
