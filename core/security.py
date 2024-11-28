from typing import Dict, Optional, Callable
import ssl
import time
from dataclasses import dataclass
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

@dataclass
class RateLimitConfig:
    requests_per_minute: int
    burst_size: Optional[int] = None

class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, Dict] = {}
        
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = {
                'count': 0,
                'last_reset': current_time
            }
            
        client = self.requests[client_ip]
        
        # Reset counter if minute has passed
        if current_time - client['last_reset'] >= 60:
            client['count'] = 0
            client['last_reset'] = current_time
            
        if client['count'] >= self.config.requests_per_minute:
            raise HTTPException(status_code=429, 
                              detail="Rate limit exceeded")
            
        client['count'] += 1

class SecurityManager:
    def __init__(self):
        self.rate_limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=60,
            burst_size=10
        ))
        self.ssl_context = self._create_ssl_context()
        self.token_validator = HTTPBearer()
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with strong security settings"""
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20')
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        return context
        
    def generate_certificate(self, common_name: str) -> Tuple[str, str]:
        """Generate self-signed certificate"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name)
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(private_key, hashes.SHA256())
        
        return (
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode(),
            cert.public_bytes(serialization.Encoding.PEM).decode()
        )
        
    async def validate_token(self, credentials: HTTPAuthorizationCredentials) -> Dict:
        """Validate JWT token"""
        try:
            payload = jwt.decode(
                credentials.credentials,
                'your-secret-key',  # Should be environment variable
                algorithms=['HS256']
            )
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
            
    def create_token(self, data: Dict) -> str:
        """Create JWT token"""
        return jwt.encode(
            data,
            'your-secret-key',  # Should be environment variable
            algorithm='HS256'
        )
        
    async def ddos_protection_middleware(self,
                                       request: Request,
                                       call_next: Callable):
        """DDoS protection middleware"""
        await self.rate_limiter.check_rate_limit(request)
        
        # Additional DDoS protection logic here
        # - Check request patterns
        # - Monitor payload sizes
        # - Track suspicious IPs
        
        response = await call_next(request)
        return response
