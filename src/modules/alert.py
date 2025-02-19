import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from config import DISCORD_WEBHOOK_URL, USER1, USER2

load_dotenv()

class AlertManager:
    def __init__(self):
        self.DISCORD_WEBHOOK_URL = DISCORD_WEBHOOK_URL

    def send_discord_alert(self, message):
        payload = {"content": message}
        response = requests.post(self.DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("✅Alert sent for:", message.split("\n")[2]) 
        else:
            print(f"Failed to send alert. Status Code: {response.status_code}")

    def send_squeeze_alerts(self, squeeze_df, days):
        if squeeze_df is None or squeeze_df.empty:
            print(f"⚠️ No squeeze signals found in the last {days} days.")
            return
        
        squeeze_df["timestamp"] = pd.to_datetime(squeeze_df["timestamp"])
        start_date = datetime.today() - timedelta(days=days)
        recent_signals = squeeze_df[squeeze_df["timestamp"] >= start_date]

        recent_signals = recent_signals.drop_duplicates(subset=["ticker"], keep="first")

        if not recent_signals.empty:
            for _, row in recent_signals.iterrows():
                ticker = row["ticker"]
                date = row["timestamp"].strftime("%Y-%m-%d")
                current_price = row["current_price"]
                take_profit = row["take_profit"]
                stop_loss = row["stop_loss"]
                user1 = USER1
                user2 = USER2

                message = (
                    "----------------------------------------\n"
                    f"🐢 hallo baozhi <@{user1}> <@{user2}> 🐢\n"
                    f"🐢 **{ticker}** fired a TTM Squeeze on {date} 🐢\n"
                    f"**Current price**: ${current_price:.2f}\n"
                    f"Hichart recommends **taking profit** at: ${take_profit:.2f}\n"
                    f"Hichart says your **stop loss** should be: ${stop_loss:.2f}\n"
                    "----------------------------------------"
                )

                self.send_discord_alert(message)

        else:
            print(f"⚠️ No squeeze signals found in the last {days} days.")