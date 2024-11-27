from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path

@dataclass
class DashboardConfig:
    network: str = "mainnet"
    api_keys: Dict[str, str] = None
    ml_models_path: str = None
    environment: str = "development"
    log_level: str = "INFO"
    metrics_enabled: bool = True
    cache_ttl: int = 3600
    max_workers: int = 4
    request_timeout: int = 30
    rate_limit: int = 100
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = {}
        if self.ml_models_path is None:
            self.ml_models_path = str(Path.home() / ".anya" / "models")
    
    @classmethod
    def load_config(cls, config_path: str = None) -> "DashboardConfig":
        """Load dashboard configuration from file or environment"""
        config_data = {}
        
        # Load from file if exists
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        
        # Override with environment variables
        env_mapping = {
            "ANYA_NETWORK": "network",
            "ANYA_ENV": "environment",
            "ANYA_LOG_LEVEL": "log_level",
            "ANYA_METRICS_ENABLED": "metrics_enabled",
            "ANYA_CACHE_TTL": "cache_ttl",
            "ANYA_MAX_WORKERS": "max_workers",
            "ANYA_REQUEST_TIMEOUT": "request_timeout",
            "ANYA_RATE_LIMIT": "rate_limit",
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                if isinstance(getattr(cls, config_key, None), bool):
                    value = value.lower() == "true"
                elif isinstance(getattr(cls, config_key, None), int):
                    value = int(value)
                config_data[config_key] = value
        
        return cls(**config_data)
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Safely retrieve API key for a service"""
        return self.api_keys.get(service)