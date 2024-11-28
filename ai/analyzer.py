from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available. Analysis features will be limited.")

@dataclass
class AnalysisResult:
    risk_score: float
    recommendations: List[str]
    predicted_trends: Dict[str, float]

class TransactionAnalyzer:
    def __init__(self):
        if not NUMPY_AVAILABLE:
            raise ImportError("Numpy is required for transaction analysis")
        self.window_size = 10
        
    def analyze_transactions(self, transactions: List[Dict]) -> AnalysisResult:
        """Analyze transaction patterns and provide insights"""
        if not transactions:
            return AnalysisResult(
                risk_score=0.0,
                recommendations=["No transactions to analyze"],
                predicted_trends={}
            )
            
        # Convert transactions to numpy arrays
        amounts = np.array([tx['amount'] for tx in transactions])
        times = np.array([tx['time'] for tx in transactions])
        
        # Basic analysis
        risk_score = self._calculate_risk_score(amounts)
        recommendations = self._generate_recommendations(amounts, times)
        trends = self._predict_trends(amounts, times)
        
        return AnalysisResult(
            risk_score=risk_score,
            recommendations=recommendations,
            predicted_trends=trends
        )
        
    def _calculate_risk_score(self, amounts: np.ndarray) -> float:
        """Calculate risk score based on transaction patterns"""
        if len(amounts) == 0:
            return 0.0
            
        volatility = np.std(amounts) if len(amounts) > 1 else 0
        avg_amount = np.mean(amounts)
        
        # Simple risk score based on volatility relative to average
        risk_score = min(1.0, volatility / (avg_amount + 1e-6))
        return float(risk_score)
        
    def _generate_recommendations(self, amounts: np.ndarray, times: np.ndarray) -> List[str]:
        """Generate recommendations based on transaction analysis"""
        recommendations = []
        
        if len(amounts) > 0:
            avg_amount = np.mean(amounts)
            recommendations.append(f"Average transaction amount: {avg_amount:.2f} BTC")
            
            if len(amounts) > 1:
                recent_trend = amounts[-1] - amounts[-2]
                if recent_trend > 0:
                    recommendations.append("Recent activity shows increasing transaction amounts")
                else:
                    recommendations.append("Recent activity shows decreasing transaction amounts")
                    
        return recommendations
        
    def _predict_trends(self, amounts: np.ndarray, times: np.ndarray) -> Dict[str, float]:
        """Predict future trends based on historical data"""
        if len(amounts) < 2:
            return {'price_trend': 0.0, 'volume_trend': 0.0}
            
        # Simple linear trend
        x = np.arange(len(amounts))
        coeffs = np.polyfit(x, amounts, deg=1)
        
        return {
            'price_trend': float(coeffs[0]),
            'volume_trend': float(np.mean(np.abs(amounts)))
        }
        
    def train_model(self, historical_data: List[Dict]):
        """Train the ML model with historical transaction data"""
        # Implementation for model training
        pass 