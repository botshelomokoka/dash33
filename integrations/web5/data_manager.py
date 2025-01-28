from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass
import aiohttp

@dataclass
class DIDDocument:
    id: str
    controller: str
    verification_methods: List[Dict]
    services: List[Dict]

@dataclass
class DWNRecord:
    id: str
    owner: str
    schema: str
    data: Dict
    created_at: datetime
    updated_at: datetime

class Web5DataManager:
    def __init__(self, dwn_endpoint: str, did: str):
        self.dwn_endpoint = dwn_endpoint
        self.did = did
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def create_record(self, 
                          schema: str,
                          data: Dict,
                          encryption_key: Optional[str] = None) -> DWNRecord:
        """Create a new DWN record"""
        payload = {
            "schema": schema,
            "data": data,
            "owner": self.did
        }
        
        if encryption_key:
            # Encrypt data if key provided
            payload["data"] = self._encrypt_data(data, encryption_key)
            
        async with self.session.post(
            f"{self.dwn_endpoint}/records",
            json=payload
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
        return DWNRecord(
            id=result["id"],
            owner=self.did,
            schema=schema,
            data=data,
            created_at=datetime.fromisoformat(result["created_at"]),
            updated_at=datetime.fromisoformat(result["updated_at"])
        )
        
    async def get_record(self, 
                        record_id: str,
                        encryption_key: Optional[str] = None) -> DWNRecord:
        """Get a DWN record by ID"""
        async with self.session.get(
            f"{self.dwn_endpoint}/records/{record_id}"
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
        data = result["data"]
        if encryption_key:
            # Decrypt data if key provided
            data = self._decrypt_data(data, encryption_key)
            
        return DWNRecord(
            id=result["id"],
            owner=result["owner"],
            schema=result["schema"],
            data=data,
            created_at=datetime.fromisoformat(result["created_at"]),
            updated_at=datetime.fromisoformat(result["updated_at"])
        )
        
    async def query_records(self, 
                          schema: Optional[str] = None,
                          filter_: Optional[Dict] = None) -> List[DWNRecord]:
        """Query DWN records"""
        params = {}
        if schema:
            params["schema"] = schema
        if filter_:
            params["filter"] = json.dumps(filter_)
            
        async with self.session.get(
            f"{self.dwn_endpoint}/records",
            params=params
        ) as response:
            response.raise_for_status()
            results = await response.json()
            
        return [
            DWNRecord(
                id=r["id"],
                owner=r["owner"],
                schema=r["schema"],
                data=r["data"],
                created_at=datetime.fromisoformat(r["created_at"]),
                updated_at=datetime.fromisoformat(r["updated_at"])
            )
            for r in results
        ]
        
    async def update_record(self,
                          record_id: str,
                          data: Dict,
                          encryption_key: Optional[str] = None) -> DWNRecord:
        """Update a DWN record"""
        payload = {"data": data}
        
        if encryption_key:
            # Encrypt data if key provided
            payload["data"] = self._encrypt_data(data, encryption_key)
            
        async with self.session.put(
            f"{self.dwn_endpoint}/records/{record_id}",
            json=payload
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
        return DWNRecord(
            id=result["id"],
            owner=self.did,
            schema=result["schema"],
            data=data,
            created_at=datetime.fromisoformat(result["created_at"]),
            updated_at=datetime.fromisoformat(result["updated_at"])
        )
        
    async def delete_record(self, record_id: str):
        """Delete a DWN record"""
        async with self.session.delete(
            f"{self.dwn_endpoint}/records/{record_id}"
        ) as response:
            response.raise_for_status()
            
    def _encrypt_data(self, data: Dict, key: str) -> Dict:
        """Encrypt data using provided key"""
        # TODO: Implement encryption
        return data
        
    def _decrypt_data(self, data: Dict, key: str) -> Dict:
        """Decrypt data using provided key"""
        # TODO: Implement decryption
        return data
