import pytest
from dash33.wallet.wallet_manager import WalletManager, WalletInfo

def test_connect_wallet(wallet_manager):
    result = wallet_manager.connect_wallet("test_wallet")
    assert result is True
    assert "test_wallet" in wallet_manager.connected_wallets

def test_connect_wallet_with_web5(wallet_manager):
    test_did = "did:web5:test123"
    result = wallet_manager.connect_wallet("test_wallet", web5_did=test_did)
    assert result is True
    wallet_data = wallet_manager.connected_wallets["test_wallet"]
    assert wallet_data["web5_enabled"] is True
    assert wallet_data["did"] == test_did

def test_lightning_config_validation(wallet_manager):
    valid_config = {
        "node_uri": "localhost:9735",
        "macaroon": "test_macaroon"
    }
    assert wallet_manager._validate_lightning_config(valid_config) is True

    invalid_config = {"node_uri": "localhost:9735"}
    assert wallet_manager._validate_lightning_config(invalid_config) is False

def test_process_bolt12_offer(wallet_manager):
    # First connect a wallet with lightning enabled
    lightning_config = {
        "node_uri": "localhost:9735",
        "macaroon": "test_macaroon"
    }
    wallet_manager.connect_wallet("test_wallet", lightning_config=lightning_config)
    
    # Test offer processing
    test_offer = "lno1qsgqsyqcyq5rqwzqfpqqp3qqqqqqqq9q9qy9qsqzpuwx3m2wgxjcpqd9h8vmmfvdjsxqzpuqw3m2wgxjcpqd9h8vmmfvdjsxqzpuqw3m2wgxjcpqd9h8vmmfvdjsxqzpu"
    result = wallet_manager.process_bolt12_offer("test_wallet", test_offer)
    assert result is not None
    assert "amount" in result
    assert "description" in result
