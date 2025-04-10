import logging
import os
import sys

from src.macd_trader.crew import TradingCrew

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run():
    stock_ticker = os.getenv("TARGET_STOCK", "NVDA.US")  # Default to NVDA.US if not set
    trade_quantity = int(os.getenv("TRADE_QUANTITY", "1"))  # Default to 10 if not set

    inputs = {"stock_ticker": stock_ticker, "quantity": trade_quantity}

    logger.info(
        f"Starting trading crew for {stock_ticker} with quantity {trade_quantity}"
    )

    try:
        trading_crew = TradingCrew()
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
