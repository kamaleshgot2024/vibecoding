# 📦 KubeGPT Installation Guide

## **Quick Install (30 seconds)**

```powershell
# 1. Navigate to project directory
cd "c:\Users\924738\OneDrive - Cognizant\Desktop\Vibe_coding\PythonCLI using KubeGPT"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify kubectl access
kubectl cluster-info

# 4. Test KubeGPT
python kubegpt.py --help
```

✅ **Done! You're ready to use KubeGPT.**

---

## **Prerequisites**

### **Required:**
- 🐍 **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- ⚙️ **kubectl** - [Installation guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)
- 🚢 **Kubernetes cluster access** (minikube, cloud cluster, etc.)

### **Optional (for AI features):**
- 🤖 **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

---

## **Detailed Installation**

### **Step 1: Python Environment Setup**

#### **Option A: Using Virtual Environment (Recommended)**
```powershell
# Create virtual environment
python -m venv kubegpt-env

# Activate (Windows)
kubegpt-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **Option B: Global Installation**
```powershell
# Install directly (simpler but less isolated)
pip install -r requirements.txt
```

### **Step 2: Verify Dependencies**
```powershell
# Test required packages
python -c "import typer, rich, openai, yaml; print('✅ All dependencies installed!')"
```

### **Step 3: Kubernetes Setup**

#### **Local Development (Minikube)**
```powershell
# Install minikube
# Download from: https://minikube.sigs.k8s.io/docs/start/

# Start cluster
minikube start

# Verify
kubectl get nodes
```

#### **Cloud Clusters**
```powershell
# AWS EKS
aws eks update-kubeconfig --region us-west-2 --name my-cluster

# Azure AKS
az aks get-credentials --resource-group myRG --name myCluster

# Google GKE
gcloud container clusters get-credentials my-cluster --zone us-central1-a
```

### **Step 4: AI Configuration (Optional)**
```powershell
# Set OpenAI API key
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

---

## **Installation Verification**

### **Basic Functionality Test**
```powershell
# Test CLI
python kubegpt.py --help

# Test kubectl integration
python kubegpt.py scan --dry-run

# Test with actual cluster
python kubegpt.py scan --problems-only
```

### **AI Features Test** (if configured)
```powershell
# Test AI integration
python kubegpt.py diagnose any-pod-name --ai --dry-run
```

---

## **Platform-Specific Notes**

### **Windows**
```powershell
# Use PowerShell or Command Prompt
# Make sure Python is in PATH
python --version

# Install kubectl via Chocolatey (optional)
choco install kubernetes-cli
```

### **Linux/WSL**
```bash
# Use bash/zsh
# Virtual environment activation:
source kubegpt-env/bin/activate

# Install kubectl (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y kubectl
```

### **macOS**
```bash
# Use Terminal
# Install kubectl via Homebrew
brew install kubectl

# Virtual environment activation:
source kubegpt-env/bin/activate
```

---

## **Docker Installation (Alternative)**

```dockerfile
# Create Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "kubegpt.py"]
```

```powershell
# Build and run
docker build -t kubegpt .
docker run -v ~/.kube:/root/.kube kubegpt --help
```

---

## **Troubleshooting Installation**

### **Common Issues:**

#### **"kubectl not found"**
```powershell
# Download kubectl manually
# Windows: https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe
# Place in PATH or project directory
```

#### **"Permission denied"**
```powershell
# Run as administrator or fix Python permissions
# Or use virtual environment
```

#### **"Module not found"**
```powershell
# Ensure you're in the right directory
cd "c:\Users\924738\OneDrive - Cognizant\Desktop\Vibe_coding\PythonCLI using KubeGPT"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **"Cluster unreachable"**
```powershell
# Check kubectl configuration
kubectl config view
kubectl config current-context

# Test connection
kubectl get pods
```

---

## **Development Installation**

For contributors and developers:

```powershell
# Clone repository (if applicable)
git clone <repo-url>
cd kubegpt

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest flake8 black

# Run tests
python -m pytest
```

---

## **Post-Installation**

### **Quick Start Commands:**
```powershell
# Show help
python kubegpt.py --help

# Scan for issues
python kubegpt.py scan

# Diagnose specific pod
python kubegpt.py diagnose pod-name

# Run innovation demo
python innovation_demo.py
```

### **Configuration:**
- 📁 Config file: `config.yaml`
- 🔑 Environment variables: `OPENAI_API_KEY`
- 📋 Logs: Check console output with `--verbose`

---

## **What's Next?**

1. ✅ **Installation complete**
2. 📖 **Read**: `HOW_TO_RUN.md` for detailed usage
3. 🎮 **Try**: `python innovation_demo.py` 
4. 🚀 **Explore**: AI-powered diagnosis with `--ai` flag
5. 🤝 **Contribute**: Add your own diagnostic patterns!

**Welcome to the future of Kubernetes troubleshooting!** 🎉