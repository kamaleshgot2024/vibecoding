#!/usr/bin/env python3
"""
KubeGPT Test Script

Simple test to verify installation and basic functionality.
"""

import sys
import subprocess
from pathlib import Path

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        "typer",
        "rich", 
        "yaml",
        "openai",
        "colorama"
    ]
    
    failed = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def test_kubectl():
    """Test if kubectl is available"""
    print("\n🔍 Testing kubectl access...")
    
    try:
        result = subprocess.run(
            ["kubectl", "version", "--client", "--short"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  ✅ kubectl is available")
            
            # Test cluster access
            try:
                cluster_result = subprocess.run(
                    ["kubectl", "cluster-info"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if cluster_result.returncode == 0:
                    print("  ✅ Kubernetes cluster is accessible")
                    return True
                else:
                    print("  ⚠️ kubectl available but cluster not accessible")
                    print(f"    Error: {cluster_result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("  ⚠️ Cluster connection timeout")
                return False
                
        else:
            print("  ❌ kubectl not available")
            return False
            
    except FileNotFoundError:
        print("  ❌ kubectl not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("  ❌ kubectl command timeout")
        return False

def test_kubegpt_import():
    """Test if KubeGPT modules can be imported"""
    print("\n🔍 Testing KubeGPT modules...")
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    modules = [
        "kubegpt",
        "kubegpt.cli",
        "kubegpt.diagnoser", 
        "kubegpt.analyzer",
        "kubegpt.recommender"
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False
    
    print("✅ All KubeGPT modules imported successfully!")
    return True

def test_basic_functionality():
    """Test basic KubeGPT functionality"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "kubegpt.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("  ✅ CLI help command works")
            return True
        else:
            print("  ❌ CLI help command failed")
            print(f"    Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing CLI: {e}")
        return False

def check_optional_features():
    """Check optional features like OpenAI API"""
    print("\n🔍 Checking optional features...")
    
    # Check OpenAI API key
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("  ✅ OpenAI API key found (AI features available)")
    else:
        print("  ⚠️ OpenAI API key not set (AI features disabled)")
        print("    Set OPENAI_API_KEY environment variable to enable AI features")
    
    return True

def main():
    """Run all tests"""
    print("🚀 KubeGPT Installation Test")
    print("=" * 40)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_dependencies,
        test_kubectl,
        test_kubegpt_import,
        test_basic_functionality,
        check_optional_features
    ]
    
    for test in tests:
        if not test():
            all_passed = False
        print()
    
    # Final result
    print("=" * 40)
    if all_passed:
        print("🎉 All tests passed! KubeGPT is ready to use.")
        print("\n📚 Next steps:")
        print("1. python kubegpt.py --help")
        print("2. python kubegpt.py scan --namespace default")
        print("3. python kubegpt.py diagnose <pod-name>")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
