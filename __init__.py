"""
33dash - Bitcoin Dashboard with AI-powered Financial Intelligence
"""

import os
import sys
from typing import List

# Required packages with Web5 support
REQUIRED_PACKAGES = {
    'bitcoin': 'python-bitcoinlib',
    'numpy': 'numpy',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'web5': 'web5',
    'did_resolver': 'did-resolver'
}

def check_dependencies() -> List[str]:
    """Check for missing required packages"""
    missing = []
    for module, package in REQUIRED_PACKAGES.items():
        try:
            __import__(module.replace('_', '-'))
        except ImportError:
            missing.append(package)
    return missing

# Check dependencies on import
missing_packages = check_dependencies()
if missing_packages:
    print(f"Warning: Missing required packages: {', '.join(missing_packages)}")
    print("Install them using: pip install " + " ".join(missing_packages))

__version__ = "0.1.0"

# Import core components
from .wallet.wallet_manager import WalletManager
from .ai.analyzer import TransactionAnalyzer
from .config import DashboardConfig
from .web.main import create_app

# Create FastAPI app instance
app = create_app()

__all__ = [
    'WalletManager',
    'TransactionAnalyzer', 
    'DashboardConfig',
    'app',
    'create_app'
] 