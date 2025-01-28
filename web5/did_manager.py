import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import aiohttp
import base58
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

@dataclass
class DIDDocument:
    id: str
    controller: str
    verification_methods: List[Dict]
    authentication: List[str]
    assertion_method: List[str]
    key_agreement: List[str]
    capability_invocation: List[str]
    capability_delegation: List[str]
    service: List[Dict]

class DIDManager:
    def __init__(self, did_resolver_endpoint: str):
        self.resolver_endpoint = did_resolver_endpoint
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def create_did(self, 
                        controller: str,
                        services: Optional[List[Dict]] = None) -> DIDDocument:
        """Create a new DID with Ed25519 key pair"""
        # Generate key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get public key in multibase format
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        multibase_pubkey = f"z{base58.b58encode(public_bytes).decode()}"
        
        # Create verification method
        verification_method = {
            "id": f"#key-1",
            "type": "Ed25519VerificationKey2020",
            "controller": controller,
            "publicKeyMultibase": multibase_pubkey
        }
        
        # Create DID Document
        did_document = {
            "controller": controller,
            "verificationMethod": [verification_method],
            "authentication": ["#key-1"],
            "assertionMethod": ["#key-1"],
            "keyAgreement": ["#key-1"],
            "capabilityInvocation": ["#key-1"],
            "capabilityDelegation": ["#key-1"],
            "service": services or []
        }
        
        # Register DID
        async with self.session.post(
            f"{self.resolver_endpoint}/1.0/create",
            json=did_document
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
        return DIDDocument(
            id=result["id"],
            controller=result["controller"],
            verification_methods=result["verificationMethod"],
            authentication=result["authentication"],
            assertion_method=result["assertionMethod"],
            key_agreement=result["keyAgreement"],
            capability_invocation=result["capabilityInvocation"],
            capability_delegation=result["capabilityDelegation"],
            service=result["service"]
        )
        
    async def resolve_did(self, did: str) -> DIDDocument:
        """Resolve a DID to its DID Document"""
        async with self.session.get(
            f"{self.resolver_endpoint}/1.0/identifiers/{did}"
        ) as response:
            response.raise_for_status()
            result = await response.json()
            did_document = result["didDocument"]
            
        return DIDDocument(
            id=did_document["id"],
            controller=did_document["controller"],
            verification_methods=did_document["verificationMethod"],
            authentication=did_document["authentication"],
            assertion_method=did_document["assertionMethod"],
            key_agreement=did_document["keyAgreement"],
            capability_invocation=did_document["capabilityInvocation"],
            capability_delegation=did_document["capabilityDelegation"],
            service=did_document["service"]
        )
        
    async def update_did_document(self, 
                                did: str,
                                document_update: Dict) -> DIDDocument:
        """Update a DID Document"""
        async with self.session.patch(
            f"{self.resolver_endpoint}/1.0/identifiers/{did}",
            json=document_update
        ) as response:
            response.raise_for_status()
            result = await response.json()
            did_document = result["didDocument"]
            
        return DIDDocument(
            id=did_document["id"],
            controller=did_document["controller"],
            verification_methods=did_document["verificationMethod"],
            authentication=did_document["authentication"],
            assertion_method=did_document["assertionMethod"],
            key_agreement=did_document["keyAgreement"],
            capability_invocation=did_document["capabilityInvocation"],
            capability_delegation=did_document["capabilityDelegation"],
            service=did_document["service"]
        )
        
    async def deactivate_did(self, did: str):
        """Deactivate a DID"""
        async with self.session.delete(
            f"{self.resolver_endpoint}/1.0/identifiers/{did}"
        ) as response:
            response.raise_for_status()
