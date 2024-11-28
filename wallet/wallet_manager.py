from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

try:
    from bitcoin.wallet import CBitcoinSecret
    from bitcoin.core import COIN, b2x
    from bitcoin.rpc import Proxy
    BITCOIN_AVAILABLE = True
except ImportError:
    BITCOIN_AVAILABLE = False
    print("Warning: bitcoin library not available. Some features may be limited.")

try:
    from lnurl import LnUrl, decode as lnurl_decode
    from bolt12 import Offer, Invoice
    LIGHTNING_AVAILABLE = True
except ImportError:
    LIGHTNING_AVAILABLE = False
    print("Warning: Lightning support not available. Some features will be limited.")

from web5.api import Web5
from web5.did import DID

@dataclass
class WalletInfo:
    address: str
    balance: float
    transactions: List[Dict[str, Any]]
    lightning_info: Optional[Dict[str, Any]] = None

class WalletManager:
    def __init__(self, network: str = "mainnet"):
        if not BITCOIN_AVAILABLE:
            raise ImportError("Bitcoin library is required for wallet management")
        self.network = network
        self.lightning_enabled = LIGHTNING_AVAILABLE
        try:
            self.web5 = Web5()
            self.web5_available = True
        except ImportError:
            self.web5_available = False
            print("Warning: Web5 not available. Some features will be limited.")
        self.connected_wallets: Dict[str, Any] = {}
        
    def connect_wallet(self, wallet_id: str, web5_did: Optional[str] = None, 
                      lightning_config: Optional[Dict] = None) -> bool:
        """Connect a wallet, optionally using Web5 DID and Lightning"""
        try:
            wallet_data = {
                'proxy': Proxy(),
                'web5_enabled': False,
                'lightning_enabled': False
            }
            
            # Handle Web5 connection
            if web5_did:
                did = DID.from_string(web5_did)
                if not did.is_valid():
                    return False
                wallet_data.update({
                    'did': web5_did,
                    'web5_enabled': True
                })
                
            # Handle Lightning connection
            if lightning_config and self.lightning_enabled:
                if self._validate_lightning_config(lightning_config):
                    wallet_data.update({
                        'lightning_config': lightning_config,
                        'lightning_enabled': True
                    })
                    
            self.connected_wallets[wallet_id] = wallet_data
            return True
        except Exception as e:
            print(f"Error connecting wallet: {e}")
            return False
            
    def _validate_lightning_config(self, config: Dict) -> bool:
        """Validate Lightning configuration"""
        required_fields = ['node_uri', 'macaroon']
        return all(field in config for field in required_fields)
        
    def process_bolt12_offer(self, wallet_id: str, offer_str: str) -> Optional[Dict]:
        """Process a Bolt12 offer"""
        if not self.lightning_enabled:
            return None
            
        try:
            wallet = self.connected_wallets.get(wallet_id)
            if not wallet or not wallet.get('lightning_enabled'):
                return None
                
            offer = Offer.from_string(offer_str)
            return {
                'amount': offer.amount,
                'description': offer.description,
                'expiry': offer.expiry,
                'node_id': offer.node_id
            }
        except Exception as e:
            print(f"Error processing Bolt12 offer: {e}")
            return None
            
    def process_lnurl(self, wallet_id: str, lnurl_str: str) -> Optional[Dict]:
        """Process an LNURL"""
        if not self.lightning_enabled:
            return None
            
        try:
            wallet = self.connected_wallets.get(wallet_id)
            if not wallet or not wallet.get('lightning_enabled'):
                return None
                
            lnurl = lnurl_decode(lnurl_str)
            return {
                'callback': lnurl.callback,
                'max_sendable': lnurl.max_sendable,
                'min_sendable': lnurl.min_sendable,
                'metadata': json.loads(lnurl.metadata)
            }
        except Exception as e:
            print(f"Error processing LNURL: {e}")
            return None
            
    def get_wallet_info(self, wallet_id: str) -> Optional[WalletInfo]:
        """Get wallet information including Lightning data"""
        if wallet_id not in self.connected_wallets:
            return None
            
        try:
            wallet_data = self.connected_wallets[wallet_id]
            proxy = wallet_data['proxy']
            
            # Get basic wallet info
            balance = proxy.getbalance()
            transactions = proxy.listtransactions()
            
            # Get Lightning info if enabled
            lightning_info = None
            if wallet_data.get('lightning_enabled'):
                lightning_info = self._get_lightning_info(wallet_data['lightning_config'])
            
            # Get Web5 data if enabled
            if wallet_data.get('web5_enabled') and self.web5_available:
                did = wallet_data['did']
                web5_records = self.web5.records.query({
                    "from": did,
                    "filter": {
                        "schema": "https://schema.org/Transaction"
                    }
                })
                
                for record in web5_records:
                    transactions.append({
                        'txid': record.id,
                        'amount': record.data.get('amount', 0),
                        'time': record.created_at,
                        'web5': True
                    })
            
            return WalletInfo(
                address=wallet_id,
                balance=balance / 100000000,  # Convert satoshis to BTC
                transactions=transactions,
                lightning_info=lightning_info
            )
        except Exception as e:
            print(f"Error getting wallet info: {e}")
            return None
            
    def _get_lightning_info(self, config: Dict) -> Dict:
        """Get Lightning node information"""
        if not self.lightning_enabled:
            return {}
            
        try:
            # Implementation depends on specific Lightning node RPC
            return {
                'node_uri': config['node_uri'],
                'channels': [],  # Implement channel fetching
                'balance': 0,    # Implement balance fetching
                'bolt12_enabled': True
            }
        except Exception as e:
            print(f"Error getting Lightning info: {e}")
            return {}