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

def create_app():
    """Create and configure the FastAPI application"""
    if not FASTAPI_AVAILABLE:
        return None

    app = FastAPI(title="33dash")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

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