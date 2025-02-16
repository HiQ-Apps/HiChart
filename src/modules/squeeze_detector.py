import sqlite3
import pandas as pd
from config import DB_PATH

class SqueezeDetector:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_tickers(self):
        self.cursor.execute("SELECT DISTINCT ticker FROM stock_prices")
        return [row[0] for row in self.cursor.fetchall()]
    

    def detect_squeeze(self, ticker):
        df = pd.read_sql(f"SELECT * FROM stock_prices WHERE ticker='{ticker}' ORDER BY timestamp", self.conn)

        if df.empty or len(df) < 20:
            print(f"Not enough data for {ticker}, skipping.")
            return None

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        df["SMA20"] = df["close"].rolling(20).mean()
        df["StdDev"] = df["close"].rolling(20).std()
        df["UpperBB"] = df["SMA20"] + (df["StdDev"] * 2)
        df["LowerBB"] = df["SMA20"] - (df["StdDev"] * 2)
        df["ATR"] = df["high"].rolling(20).mean() - df["low"].rolling(20).mean()
        df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["UpperKC"] = df["EMA20"] + (df["ATR"] * 1.5)
        df["LowerKC"] = df["EMA20"] - (df["ATR"] * 1.5)

        df["squeeze_on"] = (df["LowerBB"] > df["LowerKC"]) & (df["UpperBB"] < df["UpperKC"])
        df["squeeze_fired"] = df["squeeze_on"].shift(1) & ~df["squeeze_on"]
        df["bullish_squeeze"] = df["squeeze_fired"] & (df["close"] > df["EMA20"])

        squeeze_df = df[df["bullish_squeeze"]].reset_index()[["ticker", "timestamp", "bullish_squeeze"]]

        if not squeeze_df.empty:
            squeeze_df.to_sql("squeeze_signals", self.conn, if_exists="append", index=False)
            print(f"✅ Processed {ticker}, {squeeze_df.shape[0]} signals detected.")

        return squeeze_df

    def close_connection(self):
        self.conn.close()