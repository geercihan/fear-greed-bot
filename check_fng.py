import requests
from datetime import datetime
import os
import json

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "")

API_URL = "https://api.alternative.me/fng/"
STATE_FILE = "last_state.txt"

def get_sentiment_color(value):
    value = int(value)
    if value >= 75:
        return "🟣 Extreme Greed (Purple)"
    elif value >= 54:
        return "🟢 Greed (Green)"
    elif value >= 50:
        return "🟡 Neutral (Yellow)"
    elif value >= 25:
        return "🟠 Fear (Orange)"
    else:
        return "🔴 Extreme Fear (Red)"

def get_fng_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()["data"][0]
        return {
            "value": data["value"],
            "classification": data["value_classification"]
        }
    except Exception as e:
        print(f"❌ Error fetching FNG data: {e}")
        return None

def send_telegram_message(message):
    for chat_id in CHAT_IDS.split(","):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id.strip(),
            "text": message
        }
        try:
            response = requests.post(url, json=payload)
            if not response.ok:
                print(f"❌ Failed to send message to {chat_id}: {response.text}")
        except Exception as e:
            print(f"❌ Telegram error for {chat_id}: {e}")

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

def main():
    data = get_fng_data()
    if not data:
        return

    value = data["value"]
    classification = data["classification"]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')  # ✅ Fixed: use real time of execution

    color_label = get_sentiment_color(value)
    current_state = f"{color_label} | {classification}"
    last_state = load_last_state()

    if current_state != last_state:
        message = (
            f"🧠 Fear & Greed Index Update!\n\n"
            f"📊 Value: {value}\n"
            f"🎨 Sentiment: {color_label}\n"
            f"🕒 Timestamp: {timestamp}\n"
        )
        send_telegram_message(message)
        save_current_state(current_state)
    else:
        print("✅ No change in sentiment – no message sent.")

if __name__ == "__main__":
    main()
