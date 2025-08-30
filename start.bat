@echo off
REM KubeGPT Quick Start Script for Windows
REM This script sets up and runs KubeGPT with basic verification

echo ================================
echo   KubeGPT Quick Start
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo 💡 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Check kubectl
echo.
echo ⚙️ Checking kubectl...
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo ⚠️ kubectl not found
    echo 💡 Install from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
) else (
    echo ✅ kubectl found
)

REM Run quick verification
echo.
echo 🧪 Testing KubeGPT...
python quick_start.py

echo.
echo 🎯 Try these commands:
echo    python kubegpt.py scan
echo    python kubegpt.py --help
echo    python innovation_demo.py

pause
