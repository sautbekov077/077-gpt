import os
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

def ask_openrouter(message_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/YourBotUsername",  # можешь заменить своим
        "X-Title": "Telegram Chatbot"
    }

    data = {
        "model": "openrouter/horizon-alpha",
        "messages": [
            {"role": "user", "content": message_text}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        reply = ask_openrouter(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

print("🤖 Бот запущен и ждёт сообщений!")
bot.infinity_polling()
