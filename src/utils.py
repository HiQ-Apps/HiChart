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

def print_progress_bar(iteration, total, length=40):
    """Dynamically updates a single progress bar in the terminal."""
    progress = int(length * (iteration / total))  # Calculate progress fraction
    bar = "█" * progress + "-" * (length - progress)  # ASCII progress bar
    percent = (iteration / total) * 100  # Percentage completion
    sys.stdout.write(f"\rUpdating: |{bar}| {percent:.2f}% ({iteration}/{total}) ")
    sys.stdout.flush()  # Force immediate update