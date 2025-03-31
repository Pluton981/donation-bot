import logging
import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TOKEN")
DA_SECRET = os.environ.get("DA_SECRET")

if not TELEGRAM_TOKEN or not DA_SECRET:
    raise ValueError("❌ Отсутствует TELEGRAM TOKEN или DA SECRET")

# Настройка
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Данные
donations = []
MIN_AMOUNT = 0.15
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DA_EXPECTED_CURRENCY = "USD"

@app.route("/")
def home():
    return "✅ Бот работает!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    headers = request.headers

    if headers.get("Authorization") != f"Bearer {DA_SECRET}":
        return "Unauthorized", 403

    if data and 'username' in data and 'amount' in data:
        username = data['username'].lstrip('@').lower()
        amount = float(data['amount'])
        currency = data.get("currency", "").upper()

        if currency == DA_EXPECTED_CURRENCY:
            donations.append({'username': username, 'amount': amount})
            logging.info(f"💸 Новый донат: {username} — {amount} {currency}")

    return "OK", 200

def start(update, context):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", url="https://www.donationalerts.com/r/archive_unlock?v=2")],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день.\n"
    )
    update.message.reply_text(message)

    with open("kaspi.jpg", "rb") as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)

    after_image = (
        "\nОдин образ.\n"
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
        f"💵 Чтобы получить доступ:\n"
        f"Закрытый доступ к инструкции — ${MIN_AMOUNT}\n\n"
        "1⃣ Нажми [ОПЛАТИТЬ] и сделай перевод\n"
        "2⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
        "3⃣ После оплаты нажми [✅ Я оплатил]\n"
        "4⃣ Получи ссылку на материал"
    )

    update.message.reply_text(after_image, reply_markup=reply_markup)

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо! Вот ссылка: {CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Укажи @username и сумму от $0.15.")

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

def clear_donations():
    donations.clear()
    logging.info("🧹 Донаты очищены")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(clear_donations, "interval", hours=12)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
