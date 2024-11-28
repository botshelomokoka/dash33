import pytest
import torch
import numpy as np
from dash33.ai.models import (
    TransactionEncoder,
    AnomalyDetector,
    PortfolioOptimizer,
    preprocess_transaction,
    detect_anomalies,
    optimize_portfolio
)

@pytest.fixture
def transaction_encoder():
    return TransactionEncoder()

@pytest.fixture
def anomaly_detector():
    return AnomalyDetector()

@pytest.fixture
def portfolio_optimizer():
    return PortfolioOptimizer(num_assets=5)

@pytest.fixture
def sample_transaction():
    return {
        'amount': 1.0,
        'fee': 0.001,
        'confirmations': 6,
        'time': 1000000,
        'size': 225
    }

def test_transaction_encoder(transaction_encoder):
    batch_size = 10
    input_dim = 5
    x = torch.randn(batch_size, input_dim)
    
    encoded = transaction_encoder(x)
    assert encoded.shape == (batch_size, 16)  # hidden_dim // 4

def test_anomaly_detector(anomaly_detector):
    batch_size = 10
    input_dim = 5
    x = torch.randn(batch_size, input_dim)
    
    encoded, decoded = anomaly_detector(x)
    assert encoded.shape == (batch_size, 16)  # hidden_dim // 4
    assert decoded.shape == x.shape

def test_portfolio_optimizer(portfolio_optimizer):
    batch_size = 10
    num_assets = 5
    returns = torch.randn(batch_size, num_assets)
    risks = torch.randn(batch_size, num_assets)
    
    allocations = portfolio_optimizer(returns, risks)
    assert allocations.shape == (batch_size, num_assets)
    assert torch.allclose(allocations.sum(dim=1), torch.ones(batch_size))

def test_preprocess_transaction(sample_transaction):
    features = preprocess_transaction(sample_transaction)
    assert isinstance(features, np.ndarray)
    assert features.shape == (5,)
    assert features.dtype == np.float32

def test_detect_anomalies(anomaly_detector):
    transactions = [
        {'amount': 1.0, 'fee': 0.001, 'confirmations': 6, 'time': 1000000, 'size': 225},
        {'amount': 100.0, 'fee': 0.1, 'confirmations': 1, 'time': 1000100, 'size': 500},
        {'amount': 1.5, 'fee': 0.001, 'confirmations': 3, 'time': 1000200, 'size': 225}
    ]
    
    results = detect_anomalies(anomaly_detector, transactions)
    assert len(results) == len(transactions)
    assert isinstance(results[0], bool)

def test_optimize_portfolio():
    num_assets = 5
    returns = np.random.randn(num_assets)
    risks = np.abs(np.random.randn(num_assets))
    
    optimizer = PortfolioOptimizer(num_assets=num_assets)
    allocations = optimize_portfolio(optimizer, returns, risks)
    
    assert isinstance(allocations, np.ndarray)
    assert allocations.shape == (num_assets,)
    assert np.allclose(np.sum(allocations), 1.0)
    assert np.all(allocations >= 0)  # Check non-negative weights
