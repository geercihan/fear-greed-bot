import requests
from datetime import datetime
import pytz
import os

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS")
API_KEY = os.getenv("API_KEY")

API_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed"
HEADERS = {"X-CMC_PRO_API_KEY": API_KEY}

def get_sentiment_color(classification):
    sentiment_map = {
        "Extreme Fear": ("🔴", "Extreme Fear"),
        "Fear": ("🟠", "Fear"),
        "Neutral": ("🟡", "Neutral"),
        "Greed": ("🟢", "Greed"),
        "Extreme Greed": ("🟣", "Extreme Greed")  # Purple circle instead of blue
    }
    return sentiment_map.get(classification, ("⚪", "Unknown"))

def fetch_fng_data():
    response = requests.get(API_URL, headers=HEADERS)
    data = response.json()
    latest = data["data"][0]
    return {
        "value": latest["value"],
        "classification": latest["value_classification"],
        "timestamp": latest["timestamp"]
    }

def convert_timestamp_to_tunis_time(utc_timestamp):
    utc_dt = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    tunis_tz = pytz.timezone("Africa/Tunis")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(tunis_tz).strftime('%Y-%m-%d %H:%M')

def send_telegram_message(message):
    for chat_id in CHAT_IDS.split(","):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id.strip(), "text": message}
        requests.post(url, data=payload)

def main():
    data = fetch_fng_data()
    value = data["value"]
    classification = data["classification"]
    timestamp = convert_timestamp_to_tunis_time(data["timestamp"])
    color, label = get_sentiment_color(classification)

    message = (
        "🧠 Fear & Greed Index Update!\n\n"
        f"📊 Value: {value}\n"
        f"🎨 Sentiment: {color} {label}\n"
        f"🕒 Timestamp: {timestamp}"
    )
    send_telegram_message(message)

if __name__ == "__main__":
    main()
