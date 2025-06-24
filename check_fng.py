import requests
import os
from datetime import datetime
import json

# Load environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS')
API_KEY = os.getenv('API_KEY')
STATE_FILE = "last_state.json"

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
FNG_URL = "https://pro-api.coinmarketcap.com/v1/data/fng"

def get_sentiment_color(value):
    """Classify index value into sentiment and assign emoji"""
    if value >= 75:
        return "🤑 Extreme Greed (Dark Green)"
    elif value >= 54:
        return "🟢 Greed (Green)"
    elif value >= 46:
        return "🟡 Neutral (Yellow)"
    elif value >= 25:
        return "🟠 Fear (Orange)"
    else:
        return "🔴 Extreme Fear (Red)"

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            return file.read().strip()
    return ""

def save_current_state(state):
    with open(STATE_FILE, 'w') as file:
        file.write(state)

def send_telegram_message(message):
    for chat_id in CHAT_IDS.split(','):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id.strip(),
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)

def get_fng_data():
    headers = {
        "X-CMC_PRO_API_KEY": API_KEY
    }
    response = requests.get(FNG_URL, headers=headers)
    response.raise_for_status()
    data = response.json()["data"][0]
    return int(data["value"]), data["value_classification"], int(data["timestamp"])

def main():
    try:
        value, classification, timestamp_raw = get_fng_data()
        timestamp = datetime.fromtimestamp(timestamp_raw).strftime('%Y-%m-%d %H:%M')
        sentiment = get_sentiment_color(value)

        current_state = f"{sentiment} | {classification}"
        last_state = load_last_state()

        if current_state != last_state:
            message = (
                "🧠 <b>Fear & Greed Index Update!</b>\n\n"
                f"📊 <b>Value:</b> {value}\n"
                f"🎨 <b>Sentiment:</b> {sentiment}\n"
                f"⏰ <b>Timestamp:</b> {timestamp}"
            )
            send_telegram_message(message)
            save_current_state(current_state)
        else:
            print("✅ No change in sentiment — no message sent.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
