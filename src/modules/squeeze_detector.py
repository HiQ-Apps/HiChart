import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from config import DB_PATH

class SqueezeDetector:
    """
    Detects TTM Squeeze conditions using daily OHLC data.
    - "SQUEEZE ON" → Bollinger Bands inside Keltner Channels (compression)
    - "BULLISH SIGNAL" → Bollinger Bands expand past Keltner Channels with confirmation
    """

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_tickers(self):
        """Fetch all unique tickers from the stock_prices table."""
        self.cursor.execute("SELECT DISTINCT ticker FROM stock_prices")
        return [row[0] for row in self.cursor.fetchall()]
    
    def detect_squeeze(self, ticker):
        """Identifies squeeze setups using daily closing prices."""
        df = pd.read_sql(f"SELECT * FROM stock_prices WHERE ticker='{ticker}' ORDER BY timestamp", self.conn)

        if df.empty or len(df) < 21:
            print(f"Not enough data for {ticker}, skipping.")
            return None

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        # Bollinger Bands Calculation
        df["SMA20"] = df["close"].rolling(20).mean()
        df["StdDev"] = df["close"].rolling(20).std()
        df["UpperBB"] = df["SMA20"] + (df["StdDev"] * 2)
        df["LowerBB"] = df["SMA20"] - (df["StdDev"] * 2)

        # ATR Calculation (Wilder's Smoothed)
        df["ATR"] = self._calculate_atr(df["high"], df["low"], df["close"], atr_lookback=10)

        # Keltner Channel Calculation
        df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["UpperKC"], df["LowerKC"] = self._calculate_keltner_channels(df["high"], df["low"], df["close"], df["ATR"])

        df["vol_SMA"] = df["volume"].rolling(20).mean()
        df["high_RVol"] = df["volume"] > (df["vol_SMA"] * 1.5)

        df["squeeze_on"] = (df["LowerBB"] > df["LowerKC"]) & (df["UpperBB"] < df["UpperKC"])
        df["squeeze_fired"] = df["squeeze_on"].shift(1) & ~df["squeeze_on"]
        df["bullish_squeeze"] = df["squeeze_fired"] & (df["close"] > df["EMA20"]) & df["high_RVol"]

        squeeze_df = df[df["bullish_squeeze"]].reset_index()

        if not squeeze_df.empty:
            squeeze_df["current_price"] = squeeze_df["close"]
            squeeze_df["stop_loss"] = squeeze_df["current_price"] - (0.75 * squeeze_df["ATR"])
            squeeze_df["take_profit"] = squeeze_df["current_price"] + (1.5 * squeeze_df["ATR"])

            squeeze_df = squeeze_df[["ticker", "timestamp", "current_price", "ATR", "take_profit", "stop_loss"]]
            squeeze_df.to_sql("squeeze_signals", self.conn, if_exists="append", index=False)

            print(f"✅ Processed {ticker}, {squeeze_df.shape[0]} signals detected.")

        return squeeze_df

    def _calculate_atr(self, high, low, close, atr_lookback=10):
        """Calculates ATR using Wilder’s EMA smoothing."""
        tr1 = high - low
        tr2 = np.abs(high - close.shift())
        tr3 = np.abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Wilder’s ATR smoothing
        atr = true_range.ewm(alpha=1/atr_lookback, adjust=False).mean()
        return atr

    def _calculate_keltner_channels(self, high, low, close, atr, kc_lookback=20, multiplier=1.5):
        """Calculates Keltner Channels using Wilder's ATR method."""
        kc_middle = close.ewm(span=kc_lookback, adjust=False).mean()
        kc_upper = kc_middle + (multiplier * atr)
        kc_lower = kc_middle - (multiplier * atr)
        return kc_upper, kc_lower

    def close_connection(self):
        """Closes the database connection."""
        self.conn.close()
