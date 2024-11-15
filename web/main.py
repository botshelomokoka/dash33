from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available. Web dashboard will be disabled.")

from ..wallet.wallet_manager import WalletManager
from ..ai.analyzer import TransactionAnalyzer

def create_app() -> Optional[FastAPI]:
    """Create and configure the FastAPI application"""
    if not FASTAPI_AVAILABLE:
        return None
        
    app = FastAPI(
        title="33dash Dashboard",
        description="Bitcoin dashboard with AI-powered financial intelligence",
        version="0.1.0"
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
            
    @app.post("/api/wallet/connect/{wallet_id}")
    async def connect_wallet(wallet_id: str):
        """Connect a wallet"""
        try:
            wallet_manager = WalletManager()
            if wallet_manager.connect_wallet(wallet_id):
                return {"status": "success", "wallet_id": wallet_id}
            raise HTTPException(status_code=400, detail="Failed to connect wallet")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @app.get("/api/wallet/{wallet_id}/info")
    async def get_wallet_info(wallet_id: str):
        """Get wallet information"""
        try:
            wallet_manager = WalletManager()
            info = wallet_manager.get_wallet_info(wallet_id)
            if info:
                return info
            raise HTTPException(status_code=404, detail="Wallet not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @app.get("/api/wallet/{wallet_id}/analysis")
    async def get_wallet_analysis(wallet_id: str):
        """Get wallet analysis"""
        try:
            wallet_manager = WalletManager()
            analyzer = TransactionAnalyzer()
            
            info = wallet_manager.get_wallet_info(wallet_id)
            if not info:
                raise HTTPException(status_code=404, detail="Wallet not found")
                
            analysis = analyzer.analyze_transactions(info.transactions)
            return analysis
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    return app

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
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
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    start_server() 