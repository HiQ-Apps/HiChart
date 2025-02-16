import yfinance as yf
import sqlite3
import pandas as pd

with open("tickers.txt", "r") as f:
    tickers = [line.strip() for line in f.readlines()]

start_date = "2024-06-15"
end_date = "2025-02-15"

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

def insert_data(ticker, df):
    if df.empty:
        print(f"No data available for {ticker}.")
        return

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


for ticker in tickers:
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date)

    if df.empty:
        print(f"No data available for {ticker}, skipping...")
        continue  

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)  

    insert_data(ticker, df)

conn.close()
