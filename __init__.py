"""
33dash - Bitcoin Dashboard with AI-powered Financial Intelligence
"""

# Make the package name consistent
import os
import sys

# Add the package root to the Python path
package_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from .wallet.wallet_manager import WalletManager
from .ai.analyzer import TransactionAnalyzer
from .config import DashboardConfig

__version__ = "0.1.0"
__package_name__ = "33dash"

__all__ = ['WalletManager', 'TransactionAnalyzer', 'DashboardConfig'] 