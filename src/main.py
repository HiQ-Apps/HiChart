from modules.data_fetcher import DataFetcher
from modules.alert import AlertManager
from modules.squeeze_detector import SqueezeDetector
import pandas as pd
from config import TICKERS_FILE as TICKERS, DB_PATH
import argparse
import sqlite3


def load_squeeze_signals(days):
    """Load squeeze signals from SQLite based on a given number of days."""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM squeeze_signals WHERE timestamp >= date('now', '-{days} days') ORDER BY timestamp DESC"
    squeeze_df = pd.read_sql(query, conn)
    conn.close()
    return squeeze_df

def main():
    fetcher = DataFetcher()
    detector = SqueezeDetector()
    alerts = AlertManager()

    parser = argparse.ArgumentParser(description="Run HiChart with specific modules")
    parser.add_argument("--alerts", nargs="?", const=1, type=int, help="Run alerts only")
    parser.add_argument("--update", action="store_true", help="Fetch and update stock data")
    parser.add_argument("--squeeze", action="store_true", help="Run squeeze detection")

    args = parser.parse_args()

    if args.update:
        print("🔄 Running Data Fetcher...")
        fetcher = DataFetcher()
        try:
            with open(TICKERS, "r") as f:
                tickers = [line.strip() for line in f.readlines()]
            for ticker in tickers:
                fetcher.fetch_data(ticker)
        except FileNotFoundError:
            print(f"{TICKERS} file not found. ")

    if args.squeeze:
        print("📈 Running Squeeze Strategy...")
        all_signals = []
        with open(TICKERS, "r") as f:
            tickers = [line.strip() for line in f.readlines()]
        for ticker in tickers:
            signals = detector.detect_squeeze(ticker)
            if signals is not None:
                all_signals.append(signals)

        if all_signals:
            squeeze_df = pd.concat(all_signals, ignore_index=True)
            print(squeeze_df.head())


    if args.alerts is not None:
        days = args.alerts if args.alerts else 1 
        print(f"🚨 Running Alerts for the last {days} days...")
        squeeze_df = load_squeeze_signals(days)

        if squeeze_df.empty:
            print(f"⚠️ No squeeze signals found in the last {days} days.")
        else:
            alerts.send_squeeze_alerts(squeeze_df, days=days)

    if not (args.update or args.squeeze or args.alerts):
        print( "--- running the entire pipeline --- ")
        with open(TICKERS, "r") as f:
                tickers = [line.strip() for line in f.readlines()]
        
        for ticker in tickers:
            fetcher.fetch_data(ticker)

        all_signals = []
        for ticker in tickers:
            signals = detector.detect_squeeze(ticker)
            if signals is not None:
                all_signals.append(signals)

        if all_signals:
            alerts.send_squeeze_alerts(pd.concat(all_signals, ignore_index=True))
        
        fetcher.close_connection()
        detector.close_connection()

if __name__ == "__main__":
    main()