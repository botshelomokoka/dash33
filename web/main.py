from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from ..agents.finance import FinanceAgent

# Initialize FastAPI app
app = FastAPI(
    title="33dash",
    description="Bitcoin Dashboard with AI-powered Financial Intelligence",
    version="0.1.0"
)

# Configure CORS
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
async def root():
    """Serve the main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>33dash - Bitcoin Dashboard</title>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f0f0f0;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #1a1a1a; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>33dash Bitcoin Dashboard</h1>
                <div id="wallet-status">
                    <h2>Wallet Status</h2>
                    <p>Connect your wallet to get started</p>
                </div>
                <div id="transactions">
                    <h2>Recent Transactions</h2>
                    <p>No transactions to display</p>
                </div>
            </div>
            <script>
                // Basic wallet connection check
                async function checkWalletStatus() {
                    try {
                        const response = await fetch('/api/v1/wallet/status');
                        const data = await response.json();
                        document.getElementById('wallet-status').innerHTML = 
                            `<h2>Wallet Status</h2><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    } catch (error) {
                        console.error('Error checking wallet status:', error);
                    }
                }
                
                // Check status on page load
                checkWalletStatus();
            </script>
        </body>
    </html>
    """

@app.get("/api/v1/wallet/status")
async def wallet_status():
    """Get wallet connection status"""
    return {
        "status": "disconnected",
        "network": "mainnet",
        "features": [
            "bitcoin",
            "lightning",
            "rgb",
            "dlc"
        ]
    }

@app.get("/api/v1/market/analysis/{symbol}")
async def get_market_analysis(symbol: str):
    """Get market analysis for a symbol"""
    try:
        finance_agent = FinanceAgent()
        analysis = await finance_agent.analyze_asset(symbol)
        return {
            "status": "success",
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/v1/market/update")
async def get_market_update():
    """Get general market update"""
    try:
        finance_agent = FinanceAgent()
        update = await finance_agent.get_market_update()
        return {
            "status": "success",
            "data": update
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

def start_server():
    """Start the uvicorn server"""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_server() 