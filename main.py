from data_fetcher import DataFetcher
from alert import AlertManager
from squeeze_detector import SqueezeDetector
import pandas as pd

def main():
    fetcher = DataFetcher()
    detector = SqueezeDetector()
    alerts = AlertManager()

    with open("tickers.txt", "r") as f:
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