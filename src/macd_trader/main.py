import logging
import os
import sys

from src.macd_trader.crew import TradingCrew

# Add the project root to the Python path
# This allows imports like `from my_project.crew import TradingCrew`
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(project_root))

# Load environment variables from .env file

# Import the crew after setting the path and loading env vars

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def env_check():
    env_vars = [
        "PUSHPLUS_TOKEN",
        "DEEPSEEK_API_KEY",
        "TRADE_QUANTITY",
        "TARGET_STOCK",
        # "LONGBRIDGE_API_KEY",
        # "LONGBRIDGE_API_SECRET",
        # "LONGBRIDGE_ACCESS_TOKEN",
    ]
    for env_var in env_vars:
        if not os.getenv(env_var):
            raise ValueError(f"{env_var} is not set in the environment variables.")


def run():
    """Initializes and runs the Trading Crew."""
    env_check()
    # Get inputs from environment variables or provide defaults
    stock_ticker = os.getenv("TARGET_STOCK", "NVDA")  # Default to AAPL if not set
    trade_quantity = int(os.getenv("TRADE_QUANTITY", "1"))  # Default to 10 if not set

    inputs = {"stock_ticker": stock_ticker, "quantity": trade_quantity}

    logger.info(
        f"Starting trading crew for {stock_ticker} with quantity {trade_quantity}"
    )

    try:
        # Initialize the crew
        trading_crew = TradingCrew()

        # Kick off the crew's process
        # The inputs dictionary variables ({stock_ticker}, {quantity}) will be automatically
        # interpolated into the agent goals and task descriptions where defined.
        result = trading_crew.crew().kickoff(inputs=inputs)

        logger.info("\n\nTrading Crew finished execution.")
        logger.info("Final Result:")
        logger.info(result)

    except Exception as e:
        logger.error(
            f"An error occurred while running the trading crew: {e}", exc_info=True
        )


if __name__ == "__main__":
    run()
