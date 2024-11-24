"""
33dash - Bitcoin Dashboard with AI-powered Financial Intelligence
"""

import os
import sys
from typing import List

# Required packages
REQUIRED_PACKAGES = {
    'bitcoin': 'python-bitcoinlib',
    'numpy': 'numpy',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'httpx': 'httpx'
}

def check_dependencies() -> List[str]:
    """Check for missing required packages"""
    missing = []
    for module, package in REQUIRED_PACKAGES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    return missing

# Check dependencies on import
missing_packages = check_dependencies()
if missing_packages:
    print(f"Warning: Missing required packages: {', '.join(missing_packages)}")
    print("Install them using: pip install " + " ".join(missing_packages))

# Add the package root to the Python path
package_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

try:
    from .wallet.wallet_manager import WalletManager
    from .ai.analyzer import TransactionAnalyzer
    from .config import DashboardConfig
    from .web.main import create_app
except ImportError as e:
    print(f"Warning: Some features may be limited. Error: {e}")

__version__ = "0.1.0"
__package_name__ = "33dash"

__all__ = [
    'WalletManager', 
    'TransactionAnalyzer', 
    'DashboardConfig',
    'create_app'
] 