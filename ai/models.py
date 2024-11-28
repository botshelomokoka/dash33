import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ModelPrediction:
    trend: float
    confidence: float
    anomaly_score: float
    features: Dict[str, float]

class TransactionEncoder(nn.Module):
    def __init__(self, input_dim: int = 5, hidden_dim: int = 64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim // 4)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

class AnomalyDetector(nn.Module):
    def __init__(self, input_dim: int = 5, hidden_dim: int = 64):
        super().__init__()
        self.encoder = TransactionEncoder(input_dim, hidden_dim)
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 4, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded

class PortfolioOptimizer(nn.Module):
    def __init__(self, num_assets: int = 10):
        super().__init__()
        self.allocation = nn.Sequential(
            nn.Linear(num_assets * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_assets),
            nn.Softmax(dim=1)
        )
        
    def forward(self, returns: torch.Tensor, risks: torch.Tensor) -> torch.Tensor:
        x = torch.cat([returns, risks], dim=1)
        return self.allocation(x)

def preprocess_transaction(tx: Dict) -> np.ndarray:
    """Convert transaction to model input format"""
    features = [
        float(tx.get('amount', 0)),
        float(tx.get('fee', 0)),
        float(tx.get('confirmations', 0)),
        float(tx.get('time', 0)),
        float(tx.get('size', 0))
    ]
    return np.array(features, dtype=np.float32)

def detect_anomalies(model: AnomalyDetector, 
                    transactions: List[Dict],
                    threshold: float = 0.1) -> List[bool]:
    """Detect anomalous transactions"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    results = []
    with torch.no_grad():
        for tx in transactions:
            features = preprocess_transaction(tx)
            x = torch.FloatTensor(features).unsqueeze(0).to(device)
            _, decoded = model(x)
            
            reconstruction_error = torch.mean((x - decoded) ** 2).item()
            is_anomaly = reconstruction_error > threshold
            results.append(is_anomaly)
    
    return results

def optimize_portfolio(model: PortfolioOptimizer,
                      returns: np.ndarray,
                      risks: np.ndarray) -> np.ndarray:
    """Optimize portfolio allocation"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    with torch.no_grad():
        returns_tensor = torch.FloatTensor(returns).unsqueeze(0).to(device)
        risks_tensor = torch.FloatTensor(risks).unsqueeze(0).to(device)
        allocations = model(returns_tensor, risks_tensor)
        
    return allocations.cpu().numpy().squeeze()
