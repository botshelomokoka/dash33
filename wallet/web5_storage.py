"""Web5 storage integration for dash33 wallet."""

from typing import Dict, List, Optional
from datetime import datetime
import json

from web5 import DWN, DID
from .security import WalletEncryption

class Web5WalletStorage:
    """Web5-based wallet storage implementation."""
    
    def __init__(self, did: str, encryption: Optional[WalletEncryption] = None):
        """Initialize Web5 wallet storage.
        
        Args:
            did: User's Web5 DID
            encryption: Optional encryption handler
        """
        self.did = did
        self.dwn = DWN()
        self.encryption = encryption or WalletEncryption()
        
    async def store_wallet_data(self, data: Dict) -> str:
        """Store encrypted wallet data in Web5 DWN.
        
        Args:
            data: Wallet data to store
            
        Returns:
            Record ID of stored data
        """
        # Encrypt data
        encrypted = self.encryption.encrypt_wallet_data(data)
        
        # Create metadata
        metadata = {
            "owner_did": self.did,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "encryption_type": "fernet",
            "access_control": {
                "read_access": [self.did],
                "write_access": [self.did],
                "delete_access": [self.did]
            }
        }
        
        # Store in DWN
        record_id = await self.dwn.store(
            collection="wallets",
            data=encrypted,
            metadata=metadata
        )
        
        return record_id
        
    async def get_wallet_data(self, record_id: str) -> Optional[Dict]:
        """Retrieve and decrypt wallet data.
        
        Args:
            record_id: ID of wallet record
            
        Returns:
            Decrypted wallet data or None if not found
        """
        # Get from DWN
        record = await self.dwn.get("wallets", record_id)
        if not record:
            return None
            
        # Verify access
        if self.did not in record.metadata.get("access_control", {}).get("read_access", []):
            raise PermissionError("No read access to wallet data")
            
        # Decrypt data
        decrypted = self.encryption.decrypt_wallet_data(record.data)
        return json.loads(decrypted)
        
    async def list_wallets(self) -> List[Dict]:
        """List all wallets owned by user.
        
        Returns:
            List of wallet metadata
        """
        query = {
            "owner_did": self.did
        }
        
        records = await self.dwn.query("wallets", query)
        return [
            {
                "id": r.id,
                "created_at": r.metadata["created_at"],
                "updated_at": r.metadata["updated_at"]
            }
            for r in records
        ]
        
    async def update_wallet(self, record_id: str, data: Dict) -> None:
        """Update wallet data.
        
        Args:
            record_id: ID of wallet record
            data: New wallet data
        """
        # Get existing record
        record = await self.dwn.get("wallets", record_id)
        if not record:
            raise ValueError("Wallet not found")
            
        # Verify access
        if self.did not in record.metadata.get("access_control", {}).get("write_access", []):
            raise PermissionError("No write access to wallet")
            
        # Encrypt new data
        encrypted = self.encryption.encrypt_wallet_data(data)
        
        # Update metadata
        metadata = record.metadata
        metadata["updated_at"] = datetime.utcnow().isoformat()
        
        # Store update
        await self.dwn.update(
            collection="wallets",
            record_id=record_id,
            data=encrypted,
            metadata=metadata
        )
        
    async def delete_wallet(self, record_id: str) -> None:
        """Delete wallet data.
        
        Args:
            record_id: ID of wallet record
        """
        # Get existing record
        record = await self.dwn.get("wallets", record_id)
        if not record:
            return
            
        # Verify access
        if self.did not in record.metadata.get("access_control", {}).get("delete_access", []):
            raise PermissionError("No delete access to wallet")
            
        # Delete record
        await self.dwn.delete("wallets", record_id)
