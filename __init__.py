"""
dash33 - Bitcoin Dashboard with AI-powered Financial Intelligence
Production-ready Web5 ML Infrastructure Component
"""

import os
import sys
import logging
from typing import List, Dict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=os.getenv("ANYA_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Required packages with versions
REQUIRED_PACKAGES: Dict[str, str] = {
    'bitcoin': 'python-bitcoinlib==0.11.0',
    'numpy': 'numpy==1.24.3',
    'fastapi': 'fastapi==0.68.2',
    'uvicorn': 'uvicorn==0.15.0',
    'httpx': 'httpx==0.24.0',
    'torch': 'torch==2.0.1',
    'prometheus_client': 'prometheus-client==0.17.1'
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

def setup_environment():
    """Setup the environment for dash33"""
    # Create necessary directories
    data_dir = Path.home() / ".anya"
    dirs = [
        data_dir,
        data_dir / "models",
        data_dir / "cache",
        data_dir / "logs"
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables if not set
    if "ANYA_ENV" not in os.environ:
        os.environ["ANYA_ENV"] = "development"

# Check dependencies on import
missing_packages = check_dependencies()
if missing_packages:
    logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
    logger.info("Install them using: pip install " + " ".join(missing_packages))

# Setup environment
setup_environment()

# Add the package root to the Python path
package_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

try:
    from .wallet.wallet_manager import WalletManager
    from .ai.analyzer import TransactionAnalyzer
    from .config import DashboardConfig
    from .web.main import create_app
    from .web.metrics import setup_metrics
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

# Initialize metrics if enabled
if os.getenv("ANYA_METRICS_ENABLED", "true").lower() == "true":
    setup_metrics()

__version__ = "1.1.0"  # Aligned with main project version
__package_name__ = "dash33"
__description__ = "Production-ready Web5 ML Infrastructure Component"

__all__ = [
    'WalletManager',
    'TransactionAnalyzer',
    'DashboardConfig',
    'create_app',
    'setup_metrics',
    '__version__',
    '__package_name__',
    '__description__'
]