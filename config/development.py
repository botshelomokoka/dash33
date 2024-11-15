"""Development configuration for 33dash"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "web" / "static"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
RELOAD = True

# Database settings
DB_URL = "sqlite:///./dev.db"

# API settings
API_PREFIX = "/api/v1"
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Wallet settings
DEFAULT_NETWORK = "testnet"  # Use testnet for development
SUPPORTED_NETWORKS = ["mainnet", "testnet", "regtest"]

# AI settings
AI_MODELS_PATH = BASE_DIR / "ai" / "models"
ENABLE_AI = True
DEFAULT_MODEL = "gpt-4"

# Web5 settings
WEB5_ENABLED = True
DID_RESOLVER_URL = "http://localhost:8080"

# Development specific settings
DEV_WALLET_ID = "tb1qtest..."  # Test wallet for development 