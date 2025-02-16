import requests
from dotenv import load_dotenv
import os
import requests
import sqlite3
import datetime

load_dotenv()

class DataFetcher:

    BASE_URL = "https://api.tradier.com/v1/markets/history"
    HEADERS = {"Authorization": f"Bearer {os.getenv("KEY")}", "Accept": "application/json"}

    def __init__(self, db_path="stocks.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        self.cursor.execute("""
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
        """)
        self.conn.commit()
        print("Table 'historical_data' is ready in stocks.db.")

    def get_last_stored_date(self, ticker):
        self.cursor.execute(
            "SELECT MAX(date) FROM historical_data WHERE ticker = ?", (ticker,)
        )
        result = self.cursor.fetchone()[0]
        return result if result else None  


    def fetch_data(self, ticker):
        last_stored_date = self.get_last_stored_date(ticker)
        today = datetime.datetime.today()
        today_str = today.strftime("%Y-%m-%d")

        if last_stored_date and last_stored_date >= today_str:
            print(f"⏭️ Skipping fetch: Database already up to date (Last date: {last_stored_date})")
            return None  


        if today.weekday() >= 5: 
            print(f"Skipping fetch: Today is {today.strftime('%A')}, and the market is closed.")
            return None  
        
        print(f"Fetching new data for {ticker} since last date: {last_stored_date}")
        params = {"symbol": ticker, "interval": "daily"}
        response = requests.get(self.BASE_URL, params=params, headers=self.HEADERS)

        if response.status_code == 200:
            data = response.json().get("history", {}).get("day", [])
            if not data:
                print(f"⚠️ No new data for {ticker}")
                return None

            latest_date = self._store_data(ticker, data)
            return latest_date  # Return the latest updated date
        else:
            print(f"❌ Failed to fetch data for {ticker} (HTTP {response.status_code})")
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
                (ticker, row["date"], row["open"], row["high"], row["low"], row["close"]),
            )
        self.conn.commit()
        print(f"✅ Updated {ticker}")

    def close_connection(self):
        self.conn.close()