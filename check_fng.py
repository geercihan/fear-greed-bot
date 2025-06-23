import requests
from datetime import datetime
import os

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")

API_URL = "https://api.alternative.me/fng/"
STATE_FILE = "last_state.txt"

def get_sentiment_color(value: int) -> str:
    """Classify index value into color and label."""
    if value >= 75:
        return "🟢 Extreme Greed (Light Green)"
    elif value >= 51:
        return "🟢 Greed (Green)"
    elif value == 50:
        return "🟡 Neutral (Yellow)"
    elif value >= 25:
        return "🟠 Fear (Orange)"
    else:
        return "🔴 Extreme Fear (Red)"

def load_last_state() -> str | None:
    """Load the last recorded state from file."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()

def save_current_state(state: str):
    """Save the current state to file."""
    with open(STATE_FILE, "w") as f:
        f.write(state)

def send_telegram_message(message: str):
    """Send a message to all configured Telegram chat IDs."""
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id.strip(),
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=payload
        )
        if response.status_code != 200:
            print(f"Failed to send message to {chat_id}")

def main():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()["data"][0]
    except Exception as e:
        print("❌ Error fetching API data:", e)
        return

    value = int(data["value"])
    classification = data["value_classification"]
    timestamp = datetime.fromtimestamp(int(data["timestamp"])).strftime('%Y-%m-%d %H:%M')
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

if _name_ == "_main_":
    main()
