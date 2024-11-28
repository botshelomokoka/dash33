try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available. Web features will be limited.")

import os
from pathlib import Path
from fastapi import FastAPI
import uvicorn

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title="33dash")

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/api/v1/wallet/status")
    async def wallet_status():
        return {
            "status": "ready",
            "network": "mainnet",
            "features": [
                "bitcoin",
                "lightning",
                "rgb",
                "dlc"
            ],
            "ai_enabled": True
        }

    return app

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server"""
    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)

# Only start server if file is run directly
if __name__ == "__main__":
    start_server()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard page"""
    with open(os.path.join(static_dir, "index.html")) as f:
        return f.read()

# API Routes
@app.get("/api/v1/wallet/status")
async def wallet_status():
    """Get wallet connection status"""
    return {
        "status": "ready",
        "network": "mainnet",
        "features": [
            "bitcoin",
            "lightning",
            "rgb",
            "dlc",
            "web5"
        ],
        "ai_enabled": True
    }

# ... rest of your existing routes ... 