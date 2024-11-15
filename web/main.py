from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from web5.api import Web5
from web5.did import DID

from ..wallet.wallet_manager import WalletManager
from ..ai.analyzer import TransactionAnalyzer

security = HTTPBearer(auto_error=False)

# Add version prefix to all routes
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

class APIErrorHandler:
    async def __call__(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": str(e),
                    "path": request.url.path
                }
            ) 