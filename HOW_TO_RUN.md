# 🚀 How to Run KubeGPT - Complete Setup Guide

## **Quick Start (2 Minutes)**

### **Prerequisites** ✅
- **Python 3.8+** installed
- **kubectl** installed and configured
- **Kubernetes cluster** access (minikube, cloud cluster, etc.)
- **OpenAI API key** (optional, for AI features)

### **1. Clone & Navigate**
```powershell
# If you have the project folder
cd "c:\Users\924738\OneDrive - Cognizant\Desktop\Vibe_coding\PythonCLI using KubeGPT"

# Or clone from repository
git clone <your-repo-url>
cd KubeGPT
```

### **2. Install Dependencies**
```powershell
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import typer, rich; print('✅ Dependencies installed successfully!')"
```

### **3. Verify kubectl Access**
```powershell
# Check kubectl connection
kubectl cluster-info

# Should show your cluster info - if not, configure kubectl first
```

### **4. Run KubeGPT**
```powershell
# Basic pod diagnosis
python kubegpt.py diagnose my-pod-name

# Scan for problems
python kubegpt.py scan --problems-only

# Get help
python kubegpt.py --help
```

---

## **Detailed Setup Instructions**

### **Step 1: Environment Setup** 🛠️

#### **Python Environment (Recommended)**
```powershell
# Create virtual environment
python -m venv kubegpt-env

# Activate virtual environment
# On Windows:
kubegpt-env\Scripts\activate
# On Linux/Mac:
source kubegpt-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### **Verify Installation**
```powershell
# Test basic imports
python -c "from kubegpt import cli; print('✅ KubeGPT installed successfully!')"
```

### **Step 2: Kubernetes Setup** ⚙️

#### **Option A: Local Development (Minikube)**
```powershell
# Install minikube (if not already installed)
# Download from: https://minikube.sigs.k8s.io/docs/start/

# Start minikube
minikube start

# Verify connection
kubectl get nodes
```

#### **Option B: Cloud Cluster** ☁️
```powershell
# AWS EKS
aws eks update-kubeconfig --region us-west-2 --name my-cluster

# Azure AKS  
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

# Google GKE
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Verify connection
kubectl cluster-info
```

### **Step 3: AI Configuration (Optional)** 🤖

#### **OpenAI API Setup**
```powershell
# Set environment variable for AI features
$env:OPENAI_API_KEY = "your-openai-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

#### **Test AI Integration**
```powershell
# Test AI features
python kubegpt.py diagnose test-pod --ai
```

---

## **Running KubeGPT - Command Examples** 🎯

### **Basic Commands**

#### **1. Diagnose a Specific Pod**
```powershell
# Basic diagnosis
python kubegpt.py diagnose nginx-pod

# With namespace
python kubegpt.py diagnose nginx-pod --namespace production

# With AI analysis
python kubegpt.py diagnose nginx-pod --ai --verbose
```

#### **2. Scan for Problematic Pods**
```powershell
# Scan current namespace
python kubegpt.py scan

# Scan all namespaces
python kubegpt.py scan --all

# Show only problems
python kubegpt.py scan --problems-only --ai
```

#### **3. Get Pod Logs with Analysis**
```powershell
# Basic logs
python kubegpt.py logs nginx-pod

# With AI analysis
python kubegpt.py logs nginx-pod --analyze

# Last 100 lines
python kubegpt.py logs nginx-pod --tail 100
```

#### **4. Get Pod Events**
```powershell
# Recent events
python kubegpt.py events nginx-pod

# All events in namespace
python kubegpt.py events --namespace production
```

### **Advanced Usage**

#### **1. Output Formats**
```powershell
# Rich terminal output (default)
python kubegpt.py diagnose nginx-pod --format rich

# JSON output for scripting
python kubegpt.py diagnose nginx-pod --format json

# YAML output
python kubegpt.py scan --format yaml
```

#### **2. Fix Generation**
```powershell
# Generate fixes for a pod
python kubegpt.py fix nginx-pod

# Interactive fix mode
python kubegpt.py fix nginx-pod --interactive

# High confidence fixes only
python kubegpt.py fix nginx-pod --confidence 0.9
```

---

## **Demo & Innovation Showcase** 🎮

### **Innovation Demo**
```powershell
# Run the interactive innovation demo
python innovation_demo.py
```

### **Executive Presentation**
```powershell
# Run the automated presentation
python innovation_presentation.py
```

### **Example Scenarios**
```powershell
# Run example use cases
python examples.py
```

---

## **Troubleshooting Setup Issues** 🔧

### **Common Issues & Solutions**

#### **1. kubectl Not Found**
```powershell
# Install kubectl
# Windows (using chocolatey):
choco install kubernetes-cli

# Or download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

# Verify installation
kubectl version --client
```

#### **2. Python Import Errors**
```powershell
# Ensure you're in the correct directory
cd "c:\Users\924738\OneDrive - Cognizant\Desktop\Vibe_coding\PythonCLI using KubeGPT"

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **3. Cluster Connection Issues**
```powershell
# Check kubectl configuration
kubectl config view

# Check current context
kubectl config current-context

# Test connection
kubectl get pods --all-namespaces
```

#### **4. AI Features Not Working**
```powershell
# Check OpenAI API key
echo $env:OPENAI_API_KEY

# Test without AI
python kubegpt.py diagnose test-pod

# Check internet connection for AI calls
ping api.openai.com
```

---

## **Development Mode** 👨‍💻

### **For Contributors/Developers**
```powershell
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Check code style
flake8 kubegpt/

# Format code
black kubegpt/
```

### **Adding Custom Patterns**
```powershell
# Edit the pattern file
notepad kubegpt/patterns.py

# Test your changes
python kubegpt.py diagnose test-pod --verbose
```

---

## **Production Deployment** 🏭

### **Docker Container**
```dockerfile
# Dockerfile (create this)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY kubegpt/ ./kubegpt/
COPY kubegpt.py .
CMD ["python", "kubegpt.py"]
```

```powershell
# Build and run
docker build -t kubegpt .
docker run -v ~/.kube:/root/.kube kubegpt diagnose my-pod
```

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Run KubeGPT Scan
  run: |
    python kubegpt.py scan --all --format json > scan-results.json
    
- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: kubegpt-scan
    path: scan-results.json
```

---

## **Getting Help** 📞

### **Built-in Help**
```powershell
# Main help
python kubegpt.py --help

# Command-specific help
python kubegpt.py diagnose --help
python kubegpt.py scan --help
python kubegpt.py logs --help
```

### **Verbose Mode**
```powershell
# Debug information
python kubegpt.py diagnose my-pod --verbose

# See kubectl commands being run
python kubegpt.py scan --verbose --all
```

### **Configuration Check**
```powershell
# Verify setup
python kubegpt.py diagnose --dry-run
```

---

## **Success Verification** ✅

Run this command to verify everything is working:

```powershell
# Complete system test
python kubegpt.py scan --all --verbose
```

**Expected Output:**
- ✅ kubectl connection successful
- ✅ Pod information retrieved
- ✅ Pattern analysis completed
- ✅ Rich terminal output displayed
- 🤖 AI analysis (if API key configured)

---

## **Next Steps** 🚀

1. **Try the examples**: `python examples.py`
2. **Run the demo**: `python innovation_demo.py`
3. **Explore AI features**: Add OpenAI API key and use `--ai` flag
4. **Join the community**: Contribute patterns and improvements
5. **Scale up**: Deploy in your production Kubernetes environment

**Welcome to the future of Kubernetes troubleshooting!** 🎉
