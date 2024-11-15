import sys
import os
from typing import Optional

# Fix imports to use correct package name
from ..wallet.wallet_manager import WalletManager
from ..ai.analyzer import TransactionAnalyzer
from ..config import DashboardConfig

def echo(message: str):
    """Simple print wrapper for CLI output"""
    print(message)

class DashboardCLI:
    def __init__(self):
        self.config = DashboardConfig.load_config()
        self.wallet_manager = WalletManager(network=self.config.network)
        self.analyzer = TransactionAnalyzer()

    def connect(self, wallet_id: str):
        """Connect a Bitcoin wallet"""
        if self.wallet_manager.connect_wallet(wallet_id):
            echo(f"Successfully connected wallet: {wallet_id}")
        else:
            echo(f"Failed to connect wallet: {wallet_id}")

    def analyze(self, wallet_id: str):
        """Analyze wallet transactions and provide insights"""
        wallet_info = self.wallet_manager.get_wallet_info(wallet_id)
        if not wallet_info:
            echo(f"Wallet not found: {wallet_id}")
            return
            
        analysis = self.analyzer.analyze_transactions(wallet_info.transactions)
        
        echo("\nAnalysis Results:")
        echo(f"Risk Score: {analysis.risk_score:.2f}")
        echo("\nRecommendations:")
        for rec in analysis.recommendations:
            echo(f"- {rec}")
        echo("\nPredicted Trends:")
        for trend, value in analysis.predicted_trends.items():
            echo(f"- {trend}: {value:.2f}")

def main():
    """Main CLI entry point"""
    dashboard = DashboardCLI()
    
    if len(sys.argv) < 2:
        echo("Usage: 33dash <command> [options]")
        sys.exit(1)
        
    command = sys.argv[1]
    if command == "connect" and len(sys.argv) > 2:
        dashboard.connect(sys.argv[2])
    elif command == "analyze" and len(sys.argv) > 2:
        dashboard.analyze(sys.argv[2])
    else:
        echo("Invalid command or missing arguments")
        sys.exit(1)

if __name__ == '__main__':
    main() 