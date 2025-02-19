import sqlite3
from config import DB_PATH
import sys
import pandas as pd

def load_squeeze_signals(days):
    """Load squeeze signals from SQLite based on a given number of days."""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM squeeze_signals WHERE timestamp >= date('now', '-{days} days') ORDER BY timestamp DESC"
    squeeze_df = pd.read_sql(query, conn)
    conn.close()
    return squeeze_df

# def print_progress_bar(iteration, total, ticker, length=40):
#     """Dynamically updates a single progress bar in the terminal."""
#     progress = int(length * (iteration / total)) 
#     bar = "🐢" * progress + "-" * (length - progress)  
#     percent = (iteration / total) * 100  
#     sys.stdout.write("\033[F\033[K")
#     sys.stdout.write("\033[F\033[K") 
#     sys.stdout.write(f"Fetching data for {ticker}...\n") 
#     sys.stdout.write("\033[K") 
#     sys.stdout.write(f"\rUpdating: |{bar}| {percent:.2f}% ({iteration}/{total}) ")
#     sys.stdout.flush() 


def print_progress_bar(iteration, total, ticker, length=100):
    """Moves a single progress bar dynamically while updating the fetching ticker."""
    progress = min(int((iteration / total) * length), length-1) 
    bar = ["="] * length  
    bar[progress] = "🐢"  

    sys.stdout.write("\r") 
    sys.stdout.write(f"Updating {ticker}...")
    sys.stdout.write(f"|{''.join(bar)}| {progress+1}/{length}")
    sys.stdout.write("\033[F\033[K") 
    sys.stdout.flush()  
