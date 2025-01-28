import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import torch
from git import Repo

@dataclass
class ModelVersion:
    version: str
    timestamp: datetime
    metrics: Dict[str, float]
    parameters: Dict[str, any]
    git_commit: str
    training_data_hash: str

class ModelVersionControl:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.versions_file = os.path.join(model_dir, "versions.json")
        self.repo = Repo(os.path.dirname(os.path.dirname(model_dir)))
        
        os.makedirs(model_dir, exist_ok=True)
        if not os.path.exists(self.versions_file):
            self._save_versions([])
            
    def save_model(self, 
                  model: torch.nn.Module,
                  metrics: Dict[str, float],
                  parameters: Dict[str, any],
                  training_data_hash: str) -> ModelVersion:
        """Save a new model version"""
        # Generate version number
        versions = self._load_versions()
        new_version = f"v{len(versions) + 1}"
        
        # Get git commit
        git_commit = self.repo.head.commit.hexsha
        
        # Create version info
        version_info = ModelVersion(
            version=new_version,
            timestamp=datetime.now(),
            metrics=metrics,
            parameters=parameters,
            git_commit=git_commit,
            training_data_hash=training_data_hash
        )
        
        # Save model weights
        model_path = os.path.join(self.model_dir, f"{new_version}.pt")
        torch.save(model.state_dict(), model_path)
        
        # Update versions file
        versions.append(self._version_to_dict(version_info))
        self._save_versions(versions)
        
        return version_info
        
    def load_model(self, 
                  model: torch.nn.Module,
                  version: Optional[str] = None) -> ModelVersion:
        """Load a specific model version"""
        versions = self._load_versions()
        
        if version is None:
            # Load latest version
            version_dict = versions[-1]
        else:
            # Load specific version
            version_dict = next(
                (v for v in versions if v["version"] == version),
                None
            )
            if version_dict is None:
                raise ValueError(f"Version {version} not found")
                
        # Load model weights
        model_path = os.path.join(self.model_dir, f"{version_dict['version']}.pt")
        model.load_state_dict(torch.load(model_path))
        
        return self._dict_to_version(version_dict)
        
    def list_versions(self) -> List[ModelVersion]:
        """List all model versions"""
        return [self._dict_to_version(v) for v in self._load_versions()]
        
    def _load_versions(self) -> List[Dict]:
        """Load versions from JSON file"""
        if not os.path.exists(self.versions_file):
            return []
        with open(self.versions_file, 'r') as f:
            return json.load(f)
            
    def _save_versions(self, versions: List[Dict]):
        """Save versions to JSON file"""
        with open(self.versions_file, 'w') as f:
            json.dump(versions, f, indent=2, default=str)
            
    def _version_to_dict(self, version: ModelVersion) -> Dict:
        """Convert ModelVersion to dictionary"""
        return {
            "version": version.version,
            "timestamp": version.timestamp.isoformat(),
            "metrics": version.metrics,
            "parameters": version.parameters,
            "git_commit": version.git_commit,
            "training_data_hash": version.training_data_hash
        }
        
    def _dict_to_version(self, d: Dict) -> ModelVersion:
        """Convert dictionary to ModelVersion"""
        return ModelVersion(
            version=d["version"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            metrics=d["metrics"],
            parameters=d["parameters"],
            git_commit=d["git_commit"],
            training_data_hash=d["training_data_hash"]
        )
