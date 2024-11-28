#!/usr/bin/env python
"""Web dashboard entry point"""
import os
import sys
from importlib import import_module

# Add the package root to the Python path
package_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# Import using importlib to handle package name starting with number
web_main = import_module("33dash.web.main")
start_server = web_main.start_server

def main():
    start_server()

if __name__ == "__main__":
    main() 