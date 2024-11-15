import uvicorn
import os
import sys
from pathlib import Path

def run_dev_server():
    """Run development server with hot reload"""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))

    # Run server
    uvicorn.run(
        "33dash.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "33dash")],
        log_level="info"
    )

if __name__ == "__main__":
    run_dev_server() 