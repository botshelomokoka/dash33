import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from dash33.core.security import SecurityManager, RateLimiter, RateLimitConfig
from dash33.wallet.security import WalletEncryption, MultiSigWallet

@pytest.fixture
def security_manager():
    return SecurityManager()

@pytest.fixture
def wallet_encryption():
    return WalletEncryption()

@pytest.fixture
def multisig_wallet():
    return MultiSigWallet(required_signatures=2, total_keys=3)

def test_rate_limiter(security_manager):
    app = FastAPI()
    client = TestClient(app)
    
    @app.get("/test")
    async def test_endpoint(request: Request):
        await security_manager.rate_limiter.check_rate_limit(request)
        return {"status": "ok"}
        
    # Should allow requests within limit
    for _ in range(60):
        response = client.get("/test")
        assert response.status_code == 200
        
    # Should block excess requests
    response = client.get("/test")
    assert response.status_code == 429

def test_wallet_encryption(wallet_encryption):
    test_data = {
        "private_key": "test_key",
        "transactions": ["tx1", "tx2"]
    }
    
    # Test encryption
    encrypted = wallet_encryption.encrypt_wallet_data(test_data)
    assert isinstance(encrypted, bytes)
    
    # Test decryption
    decrypted = wallet_encryption.decrypt_wallet_data(encrypted)
    assert decrypted == test_data

def test_multisig_wallet(multisig_wallet):
    # Test key generation
    assert len(multisig_wallet.keys) == 3
    assert len(multisig_wallet.public_keys) == 3
    
    # Test transaction signing
    test_data = b"test transaction"
    signatures = multisig_wallet.sign_transaction(test_data, [0, 1])
    assert len(signatures) == 2
    
    # Test signature verification
    assert multisig_wallet.verify_signatures(test_data, signatures, [0, 1])
    
    # Test invalid signatures
    with pytest.raises(ValueError):
        multisig_wallet.sign_transaction(test_data, [0])  # Not enough signatures

def test_token_management(security_manager):
    test_data = {"user_id": "123", "role": "admin"}
    
    # Test token creation
    token = security_manager.create_token(test_data)
    assert isinstance(token, str)
    
    # Test token validation
    class MockCredentials:
        def __init__(self, token):
            self.credentials = token
    
    credentials = MockCredentials(token)
    payload = pytest.mark.asyncio(security_manager.validate_token)(credentials)
    assert payload["user_id"] == test_data["user_id"]
    assert payload["role"] == test_data["role"]
