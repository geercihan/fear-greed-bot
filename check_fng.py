import requests
from datetime import datetime
import os
import pytz

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")
API_KEY = os.getenv("API_KEY")

API_URL = "https://api.alternative.me/fng/"

def get_sentiment_color(value):
    value = int(value)
    if value >= 75:
        return "🟢🟢 Extreme Greed (Bright Green)"
    elif value >= 54:
        return "🟢 Greed (Green)"
    elif value >= 46:
        return "🟡 Neutral (Yellow)"
    elif value >= 25:
        return "🟠 Fear (Orange)"
    else:
        return "🔴 Extreme Fear (Red)"

def get_fng_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()["data"][0]
        return data["value"], data["value_classification"], data["timestamp"]
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None, None, None

def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": message}
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"❌ Failed to send message to {chat_id}: {e}")

def get_tunis_time(utc_timestamp):
    tz = pytz.timezone("Africa/Tunis")
    dt = datetime.fromtimestamp(int(utc_timestamp), tz)
    return dt.strftime('%Y-%m-%d %H:%M')

def main():
    value, classification, timestamp = get_fng_data()
    if not value or not classification:
        return

    color_label = get_sentiment_color(value)
    local_time = get_tunis_time(timestamp)

    message = (
        "🧠 Fear & Greed Index Report\n\n"
        f"📊 Value: {value}\n"
        f"🎨 Sentiment: {color_label}\n"
        f"🕒 Time: {local_time}"
    )

    send_telegram_message(message)
    print("✅ Message sent.")

if __name__ == "__main__":
    main()
