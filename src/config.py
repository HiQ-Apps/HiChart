import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "stocks.db")
TICKERS_FILE = os.path.join(DATA_DIR, "tickers.txt")

API_KEY = os.getenv("KEY")
DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK")