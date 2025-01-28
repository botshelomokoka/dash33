import time
import psutil
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class PerformanceMetrics:
    latency_ms: float
    cpu_percent: float
    memory_mb: float
    throughput: float
    error_rate: float
    timestamp: datetime

class PerformanceMonitor:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"perf_monitor_{service_name}")
        
        # Prometheus metrics
        self.request_counter = Counter(
            'service_requests_total',
            'Total number of requests',
            ['service', 'endpoint']
        )
        self.error_counter = Counter(
            'service_errors_total',
            'Total number of errors',
            ['service', 'endpoint', 'error_type']
        )
        self.latency_histogram = Histogram(
            'request_latency_seconds',
            'Request latency in seconds',
            ['service', 'endpoint']
        )
        self.cpu_gauge = Gauge(
            'service_cpu_percent',
            'CPU usage percentage',
            ['service']
        )
        self.memory_gauge = Gauge(
            'service_memory_mb',
            'Memory usage in MB',
            ['service']
        )
        
    def start_request(self, endpoint: str) -> float:
        """Start timing a request"""
        self.request_counter.labels(self.service_name, endpoint).inc()
        return time.time()
        
    def end_request(self, start_time: float, endpoint: str):
        """End timing a request"""
        duration = time.time() - start_time
        self.latency_histogram.labels(
            self.service_name,
            endpoint
        ).observe(duration)
        
    def record_error(self, endpoint: str, error_type: str):
        """Record an error"""
        self.error_counter.labels(
            self.service_name,
            endpoint,
            error_type
        ).inc()
        
    def update_resource_usage(self):
        """Update CPU and memory metrics"""
        process = psutil.Process()
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        self.cpu_gauge.labels(self.service_name).set(cpu_percent)
        
        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        self.memory_gauge.labels(self.service_name).set(memory_mb)
        
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        # Calculate error rate
        total_requests = float(self.request_counter.labels(
            self.service_name,
            ''
        )._value.get())
        total_errors = float(self.error_counter.labels(
            self.service_name,
            '',
            ''
        )._value.get())
        error_rate = total_errors / total_requests if total_requests > 0 else 0
        
        # Calculate throughput (requests per second)
        throughput = total_requests / 60  # Assuming metrics reset every minute
        
        return PerformanceMetrics(
            latency_ms=float(self.latency_histogram.labels(
                self.service_name,
                ''
            )._sum.get() * 1000),
            cpu_percent=float(self.cpu_gauge.labels(
                self.service_name
            )._value.get()),
            memory_mb=float(self.memory_gauge.labels(
                self.service_name
            )._value.get()),
            throughput=throughput,
            error_rate=error_rate,
            timestamp=datetime.now()
        )
        
    def log_metrics(self):
        """Log current metrics"""
        metrics = self.get_metrics()
        self.logger.info(
            f"Performance metrics - Service: {self.service_name}\n"
            f"Latency: {metrics.latency_ms:.2f}ms\n"
            f"CPU: {metrics.cpu_percent:.1f}%\n"
            f"Memory: {metrics.memory_mb:.1f}MB\n"
            f"Throughput: {metrics.throughput:.2f} req/s\n"
            f"Error rate: {metrics.error_rate:.2%}"
        )
