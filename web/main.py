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

def create_app() -> Optional['FastAPI']:
    """Create and configure the FastAPI application"""
    if not FASTAPI_AVAILABLE:
        return None
        
    app = FastAPI(title="33dash Dashboard")
    
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
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def get_dashboard():
        """Serve the dashboard HTML"""
        with open(static_path / "index.html") as f:
            return f.read()
            
    @app.post("/api/wallet/connect/{wallet_id}")
    async def connect_wallet(wallet_id: str):
        """Connect a wallet"""
        wallet_manager = WalletManager()
        if wallet_manager.connect_wallet(wallet_id):
            return {"status": "success"}
        raise HTTPException(status_code=400, detail="Failed to connect wallet")
        
    @app.get("/api/wallet/{wallet_id}/info")
    async def get_wallet_info(wallet_id: str):
        """Get wallet information"""
        wallet_manager = WalletManager()
        info = wallet_manager.get_wallet_info(wallet_id)
        if info:
            return info
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    @app.get("/api/wallet/{wallet_id}/analysis")
    async def get_wallet_analysis(wallet_id: str):
        """Get wallet analysis"""
        wallet_manager = WalletManager()
        analyzer = TransactionAnalyzer()
        
        info = wallet_manager.get_wallet_info(wallet_id)
        if not info:
            raise HTTPException(status_code=404, detail="Wallet not found")
            
        analysis = analyzer.analyze_transactions(info.transactions)
        return analysis
        
    return app

def start_server():
    """Start the web server"""
    app = create_app()
    if app is None:
        print("Error: FastAPI is required for the web dashboard")
        return
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start_server() 