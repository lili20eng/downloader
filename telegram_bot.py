import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "hook")

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

MESSAGES = {
    "fa": {
        "welcome": "سلام 👋\nبرای دانلود ویدیو یا صدا از هر لینکی، روی دکمه زیر بزن تا اپ باز بشه.",
        "button": "🚀 باز کردن دانلودر",
    },
    "en": {
        "welcome": "Hi 👋\nTap the button below to open the downloader and grab video or audio from any link.",
        "button": "🚀 Open downloader",
    },
    "ru": {
        "welcome": "Привет 👋\nНажми на кнопку ниже, чтобы открыть загрузчик видео и аудио.",
        "button": "🚀 Открыть загрузчик",
    },
    "ar": {
        "welcome": "مرحباً 👋\nاضغط على الزر أدناه لفتح تطبيق تحميل الفيديو أو الصوت.",
        "button": "🚀 فتح التطبيق",
    },
}


def pick_lang(language_code):
    if not language_code:
        return "en"
    code = language_code.split("-")[0].lower()
    return code if code in MESSAGES else "en"


def send_welcome(chat_id, language_code):
    lang = pick_lang(language_code)
    text = MESSAGES[lang]["welcome"]
    button_text = MESSAGES[lang]["button"]

    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": [[
                {"text": button_text, "web_app": {"url": WEBAPP_URL}}
            ]]
        }
    }
    requests.post(f"{API_BASE}/sendMessage", json=payload, timeout=10)


def handle_update(update):
    message = update.get("message")
    if not message:
        return
    chat_id = message["chat"]["id"]
    language_code = message.get("from", {}).get("language_code")
    text = message.get("text", "")

    if text.startswith("/start"):
        send_welcome(chat_id, language_code)
    else:
        send_welcome(chat_id, language_code)


def register_webhook():
    if not BOT_TOKEN or not WEBAPP_URL:
        return
    webhook_url = f"{WEBAPP_URL}/telegram/webhook/{WEBHOOK_SECRET}"
    try:
        requests.get(f"{API_BASE}/setWebhook", params={"url": webhook_url}, timeout=10)
    except requests.RequestException:
        pass
