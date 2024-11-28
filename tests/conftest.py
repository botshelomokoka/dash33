import pytest
from fastapi.testclient import TestClient
from dash33.web.main import create_app
from dash33.wallet.wallet_manager import WalletManager
from dash33.ai.analyzer import TransactionAnalyzer

@pytest.fixture
def test_app():
    app = create_app()
    return TestClient(app)

@pytest.fixture
def wallet_manager():
    return WalletManager(network="testnet")

@pytest.fixture
def transaction_analyzer():
    return TransactionAnalyzer()

@pytest.fixture
def sample_transactions():
    return [
        {"amount": 1.0, "time": 1000000},
        {"amount": 2.0, "time": 1000100},
        {"amount": 1.5, "time": 1000200}
    ]
