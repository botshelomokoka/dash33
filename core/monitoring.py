import logging
from typing import Optional, Dict, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, start_http_server

# Initialize tracer
tracer = trace.get_tracer(__name__)

# Prometheus metrics
TRANSACTION_COUNTER = Counter(
    'dash33_transactions_total',
    'Number of transactions processed'
)

ANALYSIS_DURATION = Histogram(
    'dash33_analysis_duration_seconds',
    'Time spent analyzing transactions'
)

WALLET_OPERATIONS = Counter(
    'dash33_wallet_operations_total',
    'Number of wallet operations',
    ['operation_type']
)

def setup_monitoring(prometheus_port: int = 9090):
    """Setup monitoring endpoints"""
    start_http_server(prometheus_port)

def setup_logging(log_level: str = "INFO"):
    """Configure logging"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def trace_operation(name: str):
    """Decorator for tracing operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator
