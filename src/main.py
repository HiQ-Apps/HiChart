from modules.data_fetcher import DataFetcher
from modules.alert import AlertManager
from modules.squeeze_detector import SqueezeDetector
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
TICKERS = os.path.join(DATA_DIR, "tickers.txt")


def main():
    fetcher = DataFetcher()
    detector = SqueezeDetector()
    alerts = AlertManager()

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