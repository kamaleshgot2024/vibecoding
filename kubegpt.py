#!/usr/bin/env python3
"""
KubeGPT - AI-powered Kubernetes Pod Diagnostics CLI Tool

Entry point for the KubeGPT CLI application.
"""

import sys
from pathlib import Path

# Add the kubegpt package to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kubegpt.cli import main

if __name__ == "__main__":
    main()
