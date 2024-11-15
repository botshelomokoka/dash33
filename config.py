from dataclasses import dataclass
from typing import Dict, Any
import os
import json

@dataclass
class DashboardConfig:
    network: str = "mainnet"
    api_keys: Dict[str, str] = None
    ml_models_path: str = None
    
    @classmethod
    def load_config(cls, config_path: str = None) -> "DashboardConfig":
        """Load dashboard configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        return cls() 