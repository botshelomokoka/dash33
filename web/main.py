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

def create_app() -> Optional[FastAPI]:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="33dash Dashboard",
        description="Bitcoin dashboard with AI-powered financial intelligence",
        version="0.1.0",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json"
    )
    
    # Initialize Web5
    web5 = Web5()
    
    # Add error handling middleware
    app.middleware("http")(APIErrorHandler())
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure as needed
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def get_dashboard():
        """Serve the dashboard HTML"""
        index_path = static_path / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Dashboard template not found")
        return index_path.read_text()
            
    @app.post("/api/v1/wallet/connect/{wallet_id}")
    async def connect_wallet(wallet_id: str, token: Optional[str] = Depends(security)):
        """Connect a wallet"""
        try:
            wallet_manager = WalletManager()
            if wallet_manager.connect_wallet(wallet_id):
                return {
                    "status": "success",
                    "wallet_id": wallet_id,
                    "message": "Wallet connected successfully"
                }
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Failed to connect wallet",
                    "wallet_id": wallet_id
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": str(e),
                    "wallet_id": wallet_id
                }
            )
        
    @app.get("/api/v1/wallet/{wallet_id}/info")
    async def get_wallet_info(wallet_id: str, token: Optional[str] = Depends(security)):
        """Get wallet information"""
        try:
            wallet_manager = WalletManager()
            info = wallet_manager.get_wallet_info(wallet_id)
            if info:
                return {
                    "status": "success",
                    "data": info,
                    "wallet_id": wallet_id
                }
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Wallet not found",
                    "wallet_id": wallet_id
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": str(e),
                    "wallet_id": wallet_id
                }
            )
        
    @app.get("/api/v1/wallet/{wallet_id}/analysis")
    async def get_wallet_analysis(wallet_id: str, token: Optional[str] = Depends(security)):
        """Get wallet analysis"""
        try:
            wallet_manager = WalletManager()
            analyzer = TransactionAnalyzer()
            
            info = wallet_manager.get_wallet_info(wallet_id)
            if not info:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "message": "Wallet not found",
                        "wallet_id": wallet_id
                    }
                )
                
            analysis = analyzer.analyze_transactions(info.transactions)
            return {
                "status": "success",
                "data": analysis,
                "wallet_id": wallet_id
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": str(e),
                    "wallet_id": wallet_id
                }
            )
        
    @app.post("/api/v1/web5/connect")
    async def connect_web5(request: Request):
        """Connect using Web5 DID"""
        try:
            data = await request.json()
            did = data.get('did')
            if not did:
                raise HTTPException(status_code=400, detail="DID is required")
                
            # Verify DID
            did_instance = DID.from_string(did)
            if not did_instance.is_valid():
                raise HTTPException(status_code=400, detail="Invalid DID")
                
            # Connect wallet using DID
            wallet_manager = WalletManager()
            wallet_id = did_instance.get_address()
            
            if wallet_manager.connect_wallet(wallet_id):
                return {
                    "status": "success",
                    "did": did,
                    "wallet_id": wallet_id,
                    "message": "Web5 wallet connected successfully"
                }
            raise HTTPException(
                status_code=400,
                detail="Failed to connect Web5 wallet"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @app.get("/api/v1/web5/protocols")
    async def get_web5_protocols():
        """Get supported Web5 protocols"""
        try:
            protocols = web5.get_protocols()
            return {
                "status": "success",
                "protocols": protocols
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @app.post("/api/v1/web5/record")
    async def create_web5_record(request: Request):
        """Create a Web5 record"""
        try:
            data = await request.json()
            protocol = data.get('protocol')
            schema = data.get('schema')
            record_data = data.get('data')
            
            if not all([protocol, schema, record_data]):
                raise HTTPException(
                    status_code=400,
                    detail="Protocol, schema, and data are required"
                )
                
            record = await web5.records.create(
                protocol=protocol,
                schema=schema,
                data=record_data
            )
            
            return {
                "status": "success",
                "record_id": record.id,
                "message": "Web5 record created successfully"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    return app

def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1,
    log_level: str = "info"
):
    """Start the web server"""
    app = create_app()
    if app is None:
        print("Error: FastAPI is required for the web dashboard")
        return
        
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level
        )
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    start_server() 