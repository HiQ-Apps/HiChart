"""
Setup file for HiCharts.
You only need to run this file once to set up the database + tables
"""
import yfinance as yf
import sqlite3
import pandas as pd
import os
from config import DB_PATH, TICKERS_FILE


def load_tickers(file_path =TICKERS_FILE):
    """
    custom file tickers.txt
    """
    if not os.path.exists(file_path):
        print(f"{file_path} not found")
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]
    
def create_db(db_name=DB_PATH):
    """
    create db/tables
    """
    conn = sqlite3.connect("stocks.db")
    cursor = conn.cursor()

    cursor.execute("""
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
    conn.commit()
    conn.close()
    print("DB initialize success")

def fetch_historical_data(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            print(f"No data available for {ticker}, skipping...")
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0) 
        return df
    except Exception as e:
        print(f"error for {ticker}: {e}")
        return None

def insert_data(db_name, ticker, df):
    if df.empty:
        print(f"No data found for {ticker}.")
        return
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        for index, row in df.iterrows():
            cursor.execute("""
            INSERT INTO historical_data (ticker, date, open, high, low, close)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) 
            DO UPDATE SET 
                open=excluded.open, high=excluded.high, 
                low=excluded.low, close=excluded.close;
            """, (
                ticker, 
                index.strftime("%Y-%m-%d"), 
                row["Open"], row["High"], row["Low"], row["Close"]
            ))

        conn.commit()
        print(f"Data stored for {ticker}")
    except Exception as e:
        print(f"error inserting data for {ticker}")


def run_setup(db_name="stocks.db", tickers_file="tickers.txt", start_date="2024-06-15", end_date="2025-02-15"):
    print("Initializing setup...")
    create_db(db_name)
    tickers = load_tickers(tickers_file)
    if not tickers:
        print("No tickers found. Exiting setup.")
        return
    
    for ticker in tickers:
        print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
        df = fetch_historical_data(ticker, start_date, end_date)
        insert_data(db_name, ticker, df)
    
    print("Setup complete!")

if __name__ == "__main__":
    run_setup()