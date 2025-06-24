import requests
import os
from datetime import datetime
import pytz

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")
API_KEY = os.getenv("API_KEY")

API_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
STATE_FILE = "last_state.txt"

def get_sentiment_color(value):
    if value >= 76:
        return "🟢 Extreme Greed"
    elif value >= 56:
        return "🟢 Greed"
    elif value >= 46:
        return "🟣 Neutral"
    elif value >= 26:
        return "🟠 Fear"
    else:
        return "🔴 Extreme Fear"

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

def fetch_fng_data():
    headers = {
        "X-CMC_PRO_API_KEY": API_KEY
    }
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"][0]  # latest data point

def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)

def main():
    data = fetch_fng_data()
    value = int(data["value"])
    classification = data["value_classification"]
    
    # Convert UTC timestamp to Tunisia local time
    utc_time = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    tunis_time = utc_time.astimezone(pytz.timezone("Africa/Tunis"))
    timestamp = tunis_time.strftime("%Y-%m-%d %H:%M")

    color_label = get_sentiment_color(value)
    current_state = f"{color_label} | {classification}"
    last_state = load_last_state()

    message = (
        "<b>🧠 Fear & Greed Index Update!</b>\n\n"
        f"📊 <b>Value:</b> {value}\n"
        f"🎨 <b>Sentiment:</b> {color_label} ({classification})\n"
        f"🕒 <b>Timestamp:</b> {timestamp}"
    )

    send_telegram_message(message)
    save_current_state(current_state)

if __name__ == "__main__":
    main()
