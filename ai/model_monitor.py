import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import torch
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class ModelMetrics:
    accuracy: float
    latency_ms: float
    memory_mb: float
    prediction_drift: float
    feature_drift: Dict[str, float]
    timestamp: datetime

class ModelMonitor:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.logger = logging.getLogger(f"model_monitor_{model_id}")
        
        # Prometheus metrics
        self.prediction_counter = Counter(
            'model_predictions_total',
            'Total number of predictions',
            ['model_id']
        )
        self.latency_histogram = Histogram(
            'model_latency_seconds',
            'Model prediction latency',
            ['model_id']
        )
        self.accuracy_gauge = Gauge(
            'model_accuracy',
            'Model accuracy',
            ['model_id']
        )
        self.memory_gauge = Gauge(
            'model_memory_mb',
            'Model memory usage in MB',
            ['model_id']
        )
        
    def log_prediction(self, 
                      input_features: Dict[str, float],
                      prediction: float,
                      actual: Optional[float] = None,
                      latency_ms: float = 0.0,
                      memory_mb: float = 0.0):
        """Log a single prediction with metrics"""
        self.prediction_counter.labels(self.model_id).inc()
        self.latency_histogram.labels(self.model_id).observe(latency_ms / 1000.0)
        self.memory_gauge.labels(self.model_id).set(memory_mb)
        
        if actual is not None:
            accuracy = 1.0 - abs(prediction - actual)
            self.accuracy_gauge.labels(self.model_id).set(accuracy)
            
        self.logger.info(
            f"Prediction logged - Model: {self.model_id}, "
            f"Latency: {latency_ms}ms, Memory: {memory_mb}MB"
        )
        
    def check_drift(self, 
                   recent_predictions: List[float],
                   baseline_predictions: List[float],
                   threshold: float = 0.1) -> bool:
        """Check for prediction drift"""
        if len(recent_predictions) < 100:
            return False
            
        recent_mean = np.mean(recent_predictions)
        baseline_mean = np.mean(baseline_predictions)
        drift = abs(recent_mean - baseline_mean) / baseline_mean
        
        if drift > threshold:
            self.logger.warning(
                f"Prediction drift detected: {drift:.2%} "
                f"(threshold: {threshold:.2%})"
            )
            return True
        return False
        
    def get_metrics(self) -> ModelMetrics:
        """Get current model metrics"""
        return ModelMetrics(
            accuracy=float(self.accuracy_gauge.labels(self.model_id)._value.get()),
            latency_ms=float(self.latency_histogram.labels(self.model_id)._sum.get()),
            memory_mb=float(self.memory_gauge.labels(self.model_id)._value.get()),
            prediction_drift=0.0,  # Calculated separately
            feature_drift={},  # Calculated separately
            timestamp=datetime.now()
        )
