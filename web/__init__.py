"""Web dashboard package for 33dash"""
from .main import create_app, start_server
from .scripts.web import main as cli_main

__all__ = ['create_app', 'start_server', 'cli_main'] 