import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class AlertManager:
    def __init__(self):
        self.DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK")

    def send_discord_alert(self, message):
        payload = {"content": message}
        response = requests.post(self.DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Alert sent")
        else:
            print(f"Failed to send alert. Status Code: {response.status_code}")

    def send_squeeze_alerts(self, squeeze_df):
        if squeeze_df is None or squeeze_df.empty:
            print("No bullish squeezes found.")
            return
        
        squeeze_df["date"] = pd.to_datetime(squeeze_df["date"])
        today = datetime.today()
        two_days_ago = today - timedelta(days=5)

        recent_signals = squeeze_df[squeeze_df["date"] >= two_days_ago]
        # recent_signals = squeeze_df[squeeze_df["date"] >= "2024-10-01"]
        if not recent_signals.empty:
            for _, row in recent_signals.iterrows():
                ticker, date = row["ticker"], row["date"].strftime("%Y-%m-%d")
                message = f"**BUY**: {ticker} fired a TTM Squeeze on {date}"
                self.send_discord_alert(message)
