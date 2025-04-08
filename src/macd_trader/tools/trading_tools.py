import datetime
import logging

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


class TradingTools(BaseTool):
    name: str = "Trading Tools"
    description: str = "Tools for executing stock buy and sell orders via Longbridge."

    def __init__(self):
        config = Config.from_env()
        self.ctx = QuoteContext(config)

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

    def get_ctx(self):
        config = Config.from_env()
        return QuoteContext(config)

    def get_history(self, ticker: str, start, end) -> pd.DataFrame:
        """Fetches historical data for the specified stock ticker."""
        history: list[Candlestick] = self.get_ctx().history_candlesticks_by_date(
            symbol=ticker,
            period=Period.Day,
            adjust_type=AdjustType.NoAdjust,
            start=start,
            end=end,
        )
        """
        [Candlestick { close: 227.480, open: 235.540, low: 224.220, high: 236.160, volume: 72071197, turnover: 16405645762.000, timestamp: "2025-03-10T04:00:00Z" },
        Candlestick { close: 220.840, open: 223.805, low: 217.450, high: 225.840, volume: 76137410, turnover: 16840087008.000, timestamp: "2025-03-11T04:00:00Z" },
        Candlestick { close: 216.980, open: 220.140, low: 214.910, high: 221.750, volume: 62547467, turnover: 13610872074.000, timestamp: "2025-03-12T04:00:00Z" },
        Candlestick { close: 209.680, open: 215.950, low: 208.420, high: 216.839, volume: 61368330, turnover: 13011058349.000, timestamp: "2025-03-13T04:00:00Z" },
        Candlestick { close: 213.490, open: 211.250, low: 209.580, high: 213.950, volume: 60107582, turnover: 12770032173.000, timestamp: "2025-03-14T04:00:00Z" },
        Candlestick { close: 214.000, open: 213.310, low: 209.970, high: 215.220, volume: 48073426, turnover: 10251832689.000, timestamp: "2025-03-17T04:00:00Z" },
        Candlestick { close: 212.690, open: 214.160, low: 211.490, high: 215.150, volume: 42432426, turnover: 9040583801.000, timestamp: "2025-03-18T04:00:00Z" },
        Candlestick { close: 215.240, open: 214.220, low: 213.750, high: 218.760, volume: 54385391, turnover: 11723311543.000, timestamp: "2025-03-19T04:00:00Z" },
        Candlestick { close: 214.100, open: 213.990, low: 212.220, high: 217.490, volume: 48862947, turnover: 10475668922.000, timestamp: "2025-03-20T04:00:00Z" },
        Candlestick { close: 218.270, open: 211.560, low: 211.280, high: 218.840, volume: 94127768, turnover: 20353763162.000, timestamp: "2025-03-21T04:00:00Z" },
        Candlestick { close: 220.730, open: 221.000, low: 218.580, high: 221.480, volume: 44299483, turnover: 9749138423.000, timestamp: "2025-03-24T04:00:00Z" },
        Candlestick { close: 223.750, open: 220.770, low: 220.080, high: 224.100, volume: 34493583, turnover: 7696050395.000, timestamp: "2025-03-25T04:00:00Z" },
        Candlestick { close: 221.530, open: 223.510, low: 220.470, high: 225.020, volume: 34532656, turnover: 7684282740.000, timestamp: "2025-03-26T04:00:00Z" },
        Candlestick { close: 223.850, open: 221.390, low: 220.560, high: 224.990, volume: 37094774, turnover: 8285966169.000, timestamp: "2025-03-27T04:00:00Z" },
        Candlestick { close: 217.900, open: 221.670, low: 217.680, high: 223.810, volume: 39818617, turnover: 8734519123.000, timestamp: "2025-03-28T04:00:00Z" },
        Candlestick { close: 222.130, open: 217.005, low: 216.230, high: 225.620, volume: 65299321, turnover: 14408735869.000, timestamp: "2025-03-31T04:00:00Z" },
        Candlestick { close: 223.190, open: 219.805, low: 218.900, high: 223.680, volume: 36412740, turnover: 8095865967.000, timestamp: "2025-04-01T04:00:00Z" },
        Candlestick { close: 223.890, open: 221.315, low: 221.020, high: 225.190, volume: 35905904, turnover: 7986601150.000, timestamp: "2025-04-02T04:00:00Z" },
        Candlestick { close: 203.190, open: 205.540, low: 201.250, high: 207.490, volume: 103419006, turnover: 21117733795.000, timestamp: "2025-04-03T04:00:00Z" },
        Candlestick { close: 188.380, open: 193.890, low: 187.340, high: 199.880, volume: 125910913, turnover: 24244725108.000, timestamp: "2025-04-04T04:00:00Z" },
        Candlestick { close: 181.460, open: 177.200, low: 174.620, high: 194.150, volume: 160466286, turnover: 28974344098.000, timestamp: "2025-04-07T04:00:00Z" },
        Candlestick { close: 183.695, open: 186.520, low: 183.690, high: 190.335, volume: 40026699, turnover: 7489395729.614, timestamp: "2025-04-08T04:00:00Z" }]
        """
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

    def get_macd(self, ticker: str) -> str:
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
            # Return a structured string or dictionary string representation
            return (
                f"Latest MACD data for {ticker} ({latest_timestamp}):\n"
                f"  Close Price: ${latest_data['Close']:.2f}\n"
                f"  MACD Line: {macd_value:.4f}\n"
                f"  Signal Line: {signal_value:.4f}\n"
                f"  MACD Histogram: {hist_value:.4f}"
            )

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
