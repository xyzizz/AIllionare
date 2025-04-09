import datetime
import logging
from pprint import pp

import pandas as pd
from crewai.tools import BaseTool
from longbridge.openapi import AdjustType, Candlestick, Config, Period, QuoteContext
from pydantic import BaseModel, Field
from ta.trend import MACD

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Placeholder for Longbridge SDK initialization
# You would typically initialize the client here using credentials from .env
# Example:
# from longbridge_sdk import LongbridgeClient, Config
# config = Config(
#     app_key=os.getenv("LONGBRIDGE_APP_KEY"),
#     app_secret=os.getenv("LONGBRIDGE_APP_SECRET"),
#     access_token=os.getenv("LONGBRIDGE_ACCESS_TOKEN"),
#     # Add other necessary config parameters like region, account_id etc.
# )
# client = LongbridgeClient(config)
lb_config = Config.from_env()
lb_ctx = QuoteContext(lb_config)


class LBTradingTools(BaseTool):
    name: str = "Trading Tools"
    description: str = "Tools for executing stock buy and sell orders via Longbridge."

    def _execute_order(self, ticker: str, quantity: int, side: str) -> str:
        """Placeholder function to execute a market order."""
        action = "Bought" if side == "BUY" else "Sold"
        logging.info(f"Attempting to {side} {quantity} shares of {ticker}.")

        # --- Placeholder Longbridge Integration Start ---
        # Replace this section with actual Longbridge API calls
        try:
            # Example (replace with actual SDK usage):
            # order_request = {
            #     "symbol": ticker, # Ensure ticker format matches Longbridge requirements (e.g., AAPL.US)
            #     "order_type": "MARKET",
            #     "side": side, # "BUY" or "SELL"
            #     "submitted_quantity": str(quantity),
            #     "time_in_force": "DAY", # Or other relevant time in force
            # }
            # order_response = client.submit_order(order_request)
            # logging.info(f"Longbridge order response: {order_response}")
            # Check order_response for success/failure and order ID

            # Simulating success for now
            is_success = True
            order_id = f"mock_order_{side.lower()}_{ticker}_{quantity}"

            if is_success:
                logging.info(
                    f"Successfully {action.lower()} {quantity} shares of {ticker}. Order ID: {order_id}"
                )
                return f"Successfully {action.lower()} {quantity} shares of {ticker}. Order ID: {order_id}"
            else:
                logging.error(
                    f"Failed to {side.lower()} {quantity} shares of {ticker}."
                )
                return f"Failed to {side.lower()} {quantity} shares of {ticker}. Reason: [Check Longbridge Logs/Response]"

        except Exception as e:
            logging.error(
                f"Error during Longbridge API call for {side} order of {ticker}: {e}"
            )
            return f"Error executing {side} order for {ticker}: {e}"
        # --- Placeholder Longbridge Integration End ---

    def execute_buy_order(self, ticker: str, quantity: int) -> str:
        """Executes a market buy order for the specified stock ticker and quantity."""
        return self._execute_order(ticker, quantity, "BUY")

    def execute_sell_order(self, ticker: str, quantity: int) -> str:
        """Executes a market sell order for the specified stock ticker and quantity."""
        return self._execute_order(ticker, quantity, "SELL")

    def _run(self, ticker: str, quantity: int, side: str) -> str:
        """Runs the appropriate order execution function."""
        if side.upper() == "BUY":
            return self.execute_buy_order(ticker, quantity)
        elif side.upper() == "SELL":
            return self.execute_sell_order(ticker, quantity)
        else:
            return "Invalid side specified. Use 'BUY' or 'SELL'."


class LBQuoteHistoryInput(BaseModel):
    """Input model for fetching historical stock data."""

    ticker: str = Field(
        description="The stock ticker symbol to fetch data for. E.g., AAPL.US"
    )


class LBQuoteMACDTool(BaseTool):
    name: str = "LBQuoteHistoryTool"
    description: str = "Fetches historical stock data for a given ticker symbol."
    args_schema: type[BaseModel] = LBQuoteHistoryInput

    def get_history(self, ticker: str, start, end) -> pd.DataFrame:
        """Fetches historical data for the specified stock ticker."""
        history: list[Candlestick] = lb_ctx.history_candlesticks_by_date(
            symbol=ticker,
            period=Period.Day,
            adjust_type=AdjustType.NoAdjust,
            start=start,
            end=end,
        )
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(
            [(candle.close, candle.timestamp) for candle in history],
            columns=["Close", "timestamp"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        # df.sort_index(inplace=True)
        print(df)
        return df

    def get_macd(self, ticker: str) -> list[dict]:
        """Calculates the MACD indicator for a given stock ticker and returns the latest values."""
        hist = self.get_history(
            ticker,
            start=datetime.date.today() - datetime.timedelta(days=60),
            end=datetime.date.today(),
        )
        if hist.empty:
            return f"Could not calculate MACD for {ticker} due to data fetching issues."

        try:
            # Calculate MACD
            macd = MACD(hist["Close"])
            hist["MACD"] = macd.macd()
            hist["MACD_Signal"] = macd.macd_signal()
            hist["MACD_Hist"] = macd.macd_diff()  # Histogram

            # Get the latest values
            latest_data = hist.iloc[-1]
            latest_timestamp = hist.index[-1]
            macd_value = latest_data["MACD"]
            signal_value = latest_data["MACD_Signal"]
            hist_value = latest_data["MACD_Hist"]

            if pd.isna(macd_value) or pd.isna(signal_value):
                logging.warning(
                    f"MACD calculation resulted in NaN for {ticker}. Check data period."
                )
                return (
                    f"Could not calculate valid MACD for {ticker}. Insufficient data?"
                )

            logging.info(
                f"MACD for {ticker} ({latest_timestamp}): MACD={macd_value:.2f}, Signal={signal_value:.2f}, Hist={hist_value:.2f}"
            )
            # pd to list[dict]
            hist["timestamp"] = hist.index
            hist_list = hist.to_dict(orient="records")
            # paint

            pp(hist_list)
            return hist_list
            # Return macd values list
            # return (
            #     f"Latest MACD data for {ticker} ({latest_timestamp}):\n"
            #     f"  Close Price: ${latest_data['Close']:.2f}\n"
            #     f"  MACD Line: {macd_value:.4f}\n"
            #     f"  Signal Line: {signal_value:.4f}\n"
            #     f"  MACD Histogram: {hist_value:.4f}"
            # )

        except Exception as e:
            logging.error(f"Error calculating MACD for {ticker}: {e}")
            return f"Error calculating MACD for {ticker}: {e}"

    def _run(self, ticker: str, mode: str = "macd") -> str:
        """
        Runs the specified tool function (get_macd).
        """
        # if mode == "macd":
        return self.get_macd(ticker)
        # elif mode == "price":
        #     return self.get_stock_price(ticker)
