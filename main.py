import logging
import os
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# --- Конфиги ---
TOKEN = os.environ.get("TOKEN")
DA_TOKEN = os.environ.get("DA_TOKEN")

MIN_AMOUNT = 20
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DA_API_URL = "https://www.donationalerts.com/api/v1/alerts"

if not TOKEN or not DA_TOKEN:
    raise ValueError("❌ Отсутствует TELEGRAM TOKEN или DA TOKEN")

# --- Инициализация ---
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# --- Хранилище ---
donations_checked = set()
waiting_users = set()

# --- Основной контент ---
WELCOME_TEXT = (
    "💸 Вывод за неделю — $1 250\n"
    "Без лица.\n"
    "Без публичности.\n"
    "При трудозатратах ~30 мин в день.\n\n"
    "<a href=\"https://donation-bot-ffz2.onrender.com/static/kaspi.jpg\">\u200b</a>\n"
    "Один образ.\n"
    "Чёткая подача.\n"
    "И система, в которой каждый шаг уже расписан.\n\n"
    "Ты создаёшь модель,\n"
    "генерируешь визуал,\n"
    "отвечаешь по готовым шаблонам\n"
    "— и монетизируешь внимание.\n\n"
    "📌 Это и есть AI Girl 2.0\n\n"
    "🤖 AI Girl 2.0 — связка, которая приносит деньги\n"
    "Это пошаговая система:\n"
    "👩 Генерация и оформление модели\n"
    "📸 AI-образы и подача\n"
    "💸 Получение донатов\n\n"
    "Ты получаешь:\n"
    "• Полный план запуска\n"
    "• Все нужные инструменты\n"
    "• Шаблоны общения\n"
    "• Способ приёма оплаты\n\n"
    "Всё уже проверено. Просто действуй по инструкции.\n\n"
    "💵 Чтобы получить доступ:\n"
    "Закрытый доступ к инструкции — $20\n\n"
    "1️⃣ Нажми <a href=\"https://www.donationalerts.com/r/archive_unlock?v=2\">ОПЛАТИТЬ</a> и сделай перевод на $20\n"
    "2️⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
    "3️⃣ После оплаты нажми кнопку ниже\n"
    "4️⃣ Получи ссылку на материал 💽"
)

# --- Flask route ---
@app.route("/")
def home():
    return "✅ Бот работает"

# --- Telegram хендлеры ---
def start(update, context):
    user = update.message.from_user
    username = user.username
    if username:
        waiting_users.add(username.lower())
    keyboard = [[InlineKeyboardButton("✅ Я оплатил", callback_data="check")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup, parse_mode='HTML')
    with open("kaspi.jpg", "rb") as photo:
        update.message.reply_photo(photo)

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""
    if username in donations_checked:
        query.message.reply_text(f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
    else:
        query.message.reply_text("❌ Донат не найден. Укажи @username в комментарии к донату и сумму от $20.")

# --- Регулярная проверка донатов ---
def poll_donations():
    while True:
        headers = {"Authorization": f"Bearer {DA_TOKEN}"}
        try:
            res = requests.get(DA_API_URL, headers=headers)
            data = res.json()
            for item in data.get("data", []):
                username = item.get("username", "").lower()
                amount = float(item.get("amount", 0))
                if username in waiting_users and amount >= MIN_AMOUNT:
                    donations_checked.add(username)
                    bot.send_message(
                        chat_id=item.get("message", {}).get("chat_id", None),
                        text=f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}"
                    )
        except Exception as e:
            logging.warning(f"Ошибка при запросе к DA API: {e}")
        time.sleep(30)  # каждые 30 секунд

# --- Обработчики ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# --- Старт фонового потока ---
th = threading.Thread(target=poll_donations, daemon=True)
th.start()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
