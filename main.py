import requests
import schedule
import time
from datetime import datetime
from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID, SERP_API_KEY

bot = Bot(token=TELEGRAM_TOKEN)

collected_news = []

def fetch_news():
    global collected_news

    url = "https://serpapi.com/search.json"

    params = {
        "q": "oil Hormuz OPEC UAE Iran oil supply",
        "tbm": "nws",
        "api_key": SERP_API_KEY
    }

    response = requests.get(url, params=params).json()

    if "news_results" in response:
        for article in response["news_results"][:5]:
            title = article["title"]

            if title not in collected_news:
                collected_news.append(title)

def analyze_news(news_list):
    score = 0

    for news in news_list:
        text = news.lower()

        if any(word in text for word in ["attack", "war", "iran", "hormuz", "threat"]):
            score += 2

        if any(word in text for word in ["increase production", "output", "supply", "uae", "opec"]):
            score -= 2

    if score > 2:
        return "📈 LONG"
    elif score < -2:
        return "📉 SHORT"
    else:
        return "⚖️ NEUTRAL"

def send_report():
    global collected_news

    if not collected_news:
        return

    signal = analyze_news(collected_news)

    message = f"🛢️ OIL NEWS ({datetime.now().strftime('%H:%M')})\n\n"

    for news in collected_news[:10]:
        message += f"- {news}\n"

    message += f"\n🔎 SEGNALE: {signal}"

    bot.send_message(chat_id=CHAT_ID, text=message)

    collected_news = []

schedule.every(1).minutes.do(fetch_news)
schedule.every(15).minutes.do(send_report)

while True:
    schedule.run_pending()
    time.sleep(1)
