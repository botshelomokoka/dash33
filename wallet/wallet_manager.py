from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from bitcoin.wallet import CBitcoinSecret
    from bitcoin.core import COIN, b2x
    from bitcoin.rpc import Proxy
    BITCOIN_AVAILABLE = True
except ImportError:
    BITCOIN_AVAILABLE = False
    print("Warning: bitcoin library not available. Some features may be limited.")

@dataclass
class WalletInfo:
    address: str
    balance: float
    transactions: List[Dict[str, Any]]

class WalletManager:
    def __init__(self, network: str = "mainnet"):
        if not BITCOIN_AVAILABLE:
            raise ImportError("Bitcoin library is required for wallet management")
        self.network = network
        self.proxy = Proxy()
        self.wallets: Dict[str, CBitcoinSecret] = {}
        
    def connect_wallet(self, wallet_id: str) -> bool:
        """Connect to a Bitcoin wallet"""
        try:
            # Using python-bitcoinlib for wallet operations
            key = CBitcoinSecret(wallet_id)
            self.wallets[wallet_id] = key
            return True
        except Exception as e:
            print(f"Failed to connect wallet: {e}")
            return False
            
    def get_wallet_info(self, wallet_id: str) -> Optional[WalletInfo]:
        """Get wallet information including balance and transactions"""
        if wallet_id not in self.wallets:
            return None
            
        try:
            # Get wallet information using RPC
            address = self.wallets[wallet_id].pub.hex()
            balance = float(self.proxy.getbalance()) / COIN
            txs = self.proxy.listtransactions()
            
            return WalletInfo(
                address=address,
                balance=balance,
                transactions=[{
                    'txid': b2x(tx['txid']),
                    'amount': float(tx['amount']) / COIN,
                    'confirmations': tx['confirmations'],
                    'time': tx['time']
                } for tx in txs]
            )
        except Exception as e:
            print(f"Error getting wallet info: {e}")
            return None