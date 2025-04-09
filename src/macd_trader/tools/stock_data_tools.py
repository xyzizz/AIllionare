import logging

import pandas as pd
import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ta.trend import MACD


class StockDataToolsInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker to fetch data for.")
    mode: str = Field(
        default="macd",
        description="The mode to fetch data for. 'macd' for MACD, 'price' for stock price.",
    )


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class StockDataTools(BaseTool):
    name: str = "Stock Data Tools"
    description: str = (
        "Tools for fetching stock prices and calculating MACD technical indicator."
    )
    args_schema: type[BaseModel] = StockDataToolsInput

    def _fetch_data(
        self, stock_ticker: str, period: str = "3mo", interval: str = "1d"
    ) -> pd.DataFrame:
        """Fetches historical stock data."""
        stock = yf.Ticker(stock_ticker)
        try:
            # Fetch data for a slightly longer period initially to ensure enough data for MACD
            hist = stock.history(period=period, interval=interval)
            if hist.empty:
                logging.warning(
                    f"No history found for {stock_ticker} with period={period}, interval={interval}"
                )
                # Try fetching with a default period if the initial fetch fails
                hist = stock.history(period="1y", interval="1d")
                if hist.empty:
                    logging.error(
                        f"Could not fetch any historical data for {stock_ticker}"
                    )
                    return pd.DataFrame()
            return hist
        except Exception as e:
            logging.error(f"Error fetching history for {stock_ticker}: {e}")
            return pd.DataFrame()

    def get_stock_price(self, ticker: str) -> str:
        """Fetches the latest closing stock price for a given ticker."""
        try:
            stock = yf.Ticker(ticker)
            # Get data for the last few days to ensure we get the most recent closing price
            hist = stock.history(period="5d", interval="1d")
            if not hist.empty:
                latest_price = hist["Close"].iloc[-1]
                latest_timestamp = hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")
                logging.info(
                    f"Latest price for {ticker}: {latest_price} at {latest_timestamp}"
                )
                return f"The latest closing price for {ticker} is ${latest_price:.2f} as of {latest_timestamp}."
            else:
                # Fallback for potentially delisted or problematic tickers
                info = stock.info
                current_price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                    or info.get("previousClose")
                )
                if current_price:
                    logging.info(
                        f"Current price for {ticker} from info: {current_price}"
                    )
                    return f"The current price for {ticker} is ${current_price:.2f}."
                else:
                    logging.warning(
                        f"Could not retrieve latest closing price for {ticker}."
                    )
                    return f"Could not retrieve the latest closing price for {ticker}."
        except Exception as e:
            logging.error(f"Error fetching stock price for {ticker}: {e}")
            return f"Error fetching stock price for {ticker}: {e}"

    def get_macd(self, ticker: str) -> str:
        """Calculates the MACD indicator for a given stock ticker and returns the latest values."""
        hist = self._fetch_data(ticker)
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
            latest_timestamp = hist.index[-1].strftime("%Y-%m-%d")
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
