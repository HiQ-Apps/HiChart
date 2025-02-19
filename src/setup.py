"""
Setup file for HiCharts.
You only need to run this file once to set up the database + tables
"""
import yfinance as yf
import sqlite3
import pandas as pd
import os
from config import DB_PATH, TICKERS_FILE
import os
from config import TICKERS_FILE


def load_tickers(file_path=TICKERS_FILE):
    """
    custom file tickers.txt
    """
    if not os.path.exists(file_path):
        print(f"{file_path} not found")
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]
    
def create_db(db_name=DB_PATH):
    """ Ensure database exists and create tables if missing """
    print(f"FIRST TIME SETUP: creating db")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            ticker TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INT,
            PRIMARY KEY (ticker, timestamp)
        );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database {db_name} initialized")

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
            INSERT INTO stock_prices (ticker, timestamp, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, timestamp) 
            DO UPDATE SET 
                open=excluded.open, high=excluded.high, 
                low=excluded.low, close=excluded.close;
            """, (
                ticker, 
                index.strftime("%Y-%m-%d"),
                float(row["Open"]), 
                float(row["High"]), 
                float(row["Low"]), 
                float(row["Close"]),
                int(row['Volume'])
            ))

        conn.commit()
        conn.close()
        print(f"✅ {ticker} - stored")

    except sqlite3.Error as e:
        print(f"Error {e} inserting data for {ticker}")



def run_setup(db_name=DB_PATH, tickers_file=TICKERS_FILE, start_date="2024-06-15", end_date="2025-02-15"):
    create_db(db_name)
    tickers = load_tickers(tickers_file)
    if not tickers:
        print("No tickers found..please provide a tickers.txt file for me to parse")
        return
    
    for ticker in tickers:
        print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
        df = fetch_historical_data(ticker, start_date, end_date)
        insert_data(db_name, ticker, df)
    
    print("Setup complete!")

if __name__ == "__main__":
    run_setup()