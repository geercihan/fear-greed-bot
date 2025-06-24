import requests
import os
from datetime import datetime
import pytz
import json

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
API_KEY = os.getenv("API_KEY")
STATE_FILE = "last_state.txt"

API_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical?limit=1"

def get_sentiment_color(value):
    if value >= 76:
        return "🟣 Extreme Greed (Purple)"
    elif value >= 54:
        return "🟢 Greed (Green)"
    elif value >= 46:
        return "🔵 Neutral (Blue)"
    elif value >= 25:
        return "🟠 Fear (Orange)"
    else:
        return "🔴 Extreme Fear (Red)"

def fetch_fng_data():
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    latest = data["data"][0]
    return latest

def load_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data=data)

def main():
    data = fetch_fng_data()
    value = int(data["value"])
    classification = data["value_classification"]
    
    # Convert timestamp (in seconds) to datetime in Tunis timezone
    utc_time = datetime.utcfromtimestamp(int(data["timestamp"]))
    tz = pytz.timezone("Africa/Tunis")
    tunis_time = utc_time.replace(tzinfo=pytz.utc).astimezone(tz)
    timestamp = tunis_time.strftime('%Y-%m-%d %H:%M')

    color_label = get_sentiment_color(value)
    current_state = f"{color_label} | {classification}"

    last_state = load_last_state()

    # Always send (even if no change)
    message = (
        f"🧠 Fear & Greed Index Update!\n\n"
        f"📊 Value: {value}\n"
        f"🎨 Sentiment: {color_label}\n"
        f"🕒 Timestamp: {timestamp}\n"
    )
    send_telegram_message(message)
    save_current_state(current_state)

if __name__ == "__main__":
    main()
