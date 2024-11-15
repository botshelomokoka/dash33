from pydantic import BaseModel, Field
from typing import Optional

class WalletConnect(BaseModel):
    wallet_id: str = Field(..., min_length=26, max_length=35)
    web5_did: Optional[str] = Field(None, regex=r"^did:")

class Web5Record(BaseModel):
    protocol: str
    schema: str
    data: dict 