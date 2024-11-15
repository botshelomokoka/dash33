#!/usr/bin/env python
"""Web dashboard entry point"""
import os
import sys

# Add the package root to the Python path
package_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from dash33.web.main import start_server

def main():
    start_server()

if __name__ == "__main__":
    main() 