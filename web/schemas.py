from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from enum import Enum

class WalletType(str, Enum):
    BITCOIN = "bitcoin"
    LIGHTNING = "lightning"
    WEB5 = "web5"

class WalletConnect(BaseModel):
    wallet_id: str = Field(..., min_length=26, max_length=35)
    wallet_type: WalletType = Field(default=WalletType.BITCOIN)
    web5_did: Optional[str] = Field(None, regex=r"^did:")

    @validator('web5_did')
    def validate_web5_did(cls, v, values):
        if values.get('wallet_type') == WalletType.WEB5 and not v:
            raise ValueError("web5_did is required for Web5 wallet type")
        return v

class Web5Record(BaseModel):
    protocol: str
    schema: str
    data: Dict[str, Any]

class TransactionAnalysis(BaseModel):
    risk_score: float = Field(..., ge=0, le=1)
    recommendations: List[str]
    predicted_trends: Dict[str, float]

class DashboardData(BaseModel):
    wallet_info: Dict[str, Any]
    analysis: Optional[TransactionAnalysis]
    lightning_status: Optional[Dict[str, Any]]
    web5_status: Optional[Dict[str, Any]] 