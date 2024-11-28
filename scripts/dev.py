import uvicorn
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_dev_environment():
    """Setup development environment"""
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.parent.parent
        sys.path.append(str(project_root))

        # Create necessary directories
        dirs = [
            project_root / "33dash/ai/models",
            project_root / "33dash/web/static/components",
            project_root / "logs",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

        return True
    except Exception as e:
        logger.error(f"Failed to setup development environment: {e}")
        return False

def run_dev_server():
    """Run development server with hot reload"""
    if not setup_dev_environment():
        sys.exit(1)

    logger.info("Starting development server...")
    
    try:
        uvicorn.run(
            "33dash.web.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(Path(__file__).parent.parent)],
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dev_server() 