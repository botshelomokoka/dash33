import logging
from dataclasses import dataclass
from typing import Protocol, TypeVar
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from phi.storage.agent.sqlite import SqlAgentStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')

class FinanceProtocol(Protocol):
    def get_market_data(self) -> dict:
        ...

@dataclass
class FinanceAgent(Agent, FinanceProtocol):
    def __init__(self, db_path: str = "agents.db"):
        super().__init__(
            name="Finance Agent",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                YFinanceTools(
                    stock_price=True,
                    analyst_recommendations=True,
                    company_info=True,
                    company_news=True
                )
            ],
            instructions=[
                "Use tables to display data",
                "Always include source links",
                "Format responses in markdown"
            ],
            storage=SqlAgentStorage(
                table_name="finance_agent",
                db_file=db_path
            ),
            add_history_to_messages=True,
            markdown=True,
        )
        logger.info("Finance agent initialized")

    async def analyze_asset(self, symbol: str) -> dict:
        """Analyze a financial asset"""
        response = await self.achat(
            f"Provide a comprehensive analysis for {symbol} including:"
            f"\n- Current price and recent performance"
            f"\n- Analyst recommendations"
            f"\n- Key company information"
            f"\n- Recent news"
        )
        return response.dict()

    async def get_market_update(self) -> dict:
        """Get general market update"""
        response = await self.achat(
            "Provide a market update including:"
            "\n- Major index performance"
            "\n- Key market movers"
            "\n- Important market news"
        )
        return response.dict()

    def get_market_data(self) -> dict:
        logger.info("Fetching market data")
        response = self.query(
            "Get me a summary of:\n"
            "- Key market movers\n"
            "- Important market news"
        )
        return response.dict()