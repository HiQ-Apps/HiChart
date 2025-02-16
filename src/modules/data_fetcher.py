"""
notes:
This script fetches and updates stock prices from your ticker.txt from the Tradier API and stores it in your local SQLite DB
---------------------------
- This script assumes you are tracking multiple tickers from your "tickers.txt" file
- It's optimized to only fetch missing data to prevent extraneous API calls
- Run it after market close or early morning before the market opens to update your data according and fire signals
"""

import requests
from dotenv import load_dotenv
import pandas as pd
import requests
import sqlite3
import datetime
from config import API_KEY, DB_PATH

load_dotenv()

class DataFetcher:
    BASE_URL = "https://api.tradier.com/v1/markets/history"
    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                UNIQUE(ticker, date)
            );
        """
        )
        self.conn.commit()
        print("Table 'historical_data' is ready in stocks.db.")

    def get_last_stored_date(self, ticker):
        self.cursor.execute(
            "SELECT MAX(date) FROM historical_data WHERE ticker = ?", (ticker,)
        )
        result = self.cursor.fetchone()[0]
        return result if result else None
    
    def get_previous_business_day(self):
        today = pd.Timestamp.today().normalize()
        last_business_day = (today - pd.tseries.offsets.BDay(1)).strftime("%Y-%m-%d") #get last business day
        return last_business_day
    
    def fetch_data(self, ticker):
        last_stored_date = self.get_last_stored_date(ticker)
        last_market_date = self.get_previous_business_day()


        if last_stored_date and last_stored_date >= last_market_date:
            print(
                f"⏭️ Skipping fetch: Database already up to date (Last date: {last_stored_date})"
            )
            return None

        print(f"Fetching new data for {ticker} since last date: {last_stored_date}")
        params = {
            "symbol": ticker,
            "interval": "daily",
            "start": last_stored_date,
            "end": last_market_date
        }
        response = requests.get(self.BASE_URL, params=params, headers=self.HEADERS)

        if response.status_code == 200:
            data = response.json().get("history", {}).get("day", [])
            if not data:
                print(f"No new data found today for {ticker}")
                return None

            self._store_data(ticker, data)
        else:
            print(f"Failed to fetch data for {ticker} (HTTP {response.status_code})")
            return None

    def _store_data(self, ticker, data):
        for row in data:
            self.cursor.execute(
                """
                INSERT INTO historical_data (ticker, date, open, high, low, close)
                VALUES (?, ?, ?, ?, ?, ?) 
                ON CONFLICT(ticker, date) 
                DO UPDATE SET 
                    open=excluded.open, high=excluded.high, 
                    low=excluded.low, close=excluded.close
                """,
                (
                    ticker,
                    row["date"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                ),
            )
        self.conn.commit()
        print(f"Updated {ticker} for {self.last_market_date}")

    def close_connection(self):
        self.conn.close()
