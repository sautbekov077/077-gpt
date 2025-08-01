import os
import requests
from flask import Flask, request
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # например: https://your-bot-name.onrender.com

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# OpenRouter функция
def ask_openrouter(message_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": WEBHOOK_URL,
        "X-Title": "Telegram AI Bot"
    }

    data = {
        "model": "openrouter/horizon-alpha",
        "messages": [{"role": "user", "content": message_text}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Обработка сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        reply = ask_openrouter(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

# Webhook вход
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Unsupported Media Type', 415

# Главная страница
@app.route("/", methods=['GET'])
def index():
    return "Бот работает!"

# Установка Webhook и запуск
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
