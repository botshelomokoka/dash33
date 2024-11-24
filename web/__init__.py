"""Web interface module for 33dash"""

# Only import create_app since start_server doesn't exist
from .main import create_app

__all__ = ['create_app'] 