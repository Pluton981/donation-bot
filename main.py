import logging
import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Получаем токен из переменных окружения
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("❌ Переменная окружения 'TOKEN' не установлена!")

# Настройка логгирования и Flask
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)

# Константы
donations = []
MIN_AMOUNT = 0.15  # Минимальная сумма в USD
DA_LINK = "https://www.donationalerts.com/r/archive_unlock?v=2"
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"

@app.route('/')
def home():
    return '✅ Бот успешно работает!'

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"💸 Донат: {username} — {amount}$")
    return "OK", 200

def start(update, context):
    keyboard = [[InlineKeyboardButton("💸 ОПЛАТИТЬ", url=DA_LINK)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "👋 Добро пожаловать! Чтобы получить доступ к эксклюзивному материалу, выполни следующие шаги:\n\n"
        f"1️⃣ Перейди по кнопке \"💸 ОПЛАТИТЬ\" и сделай донат от ${0.15} через DonationAlerts.\n"
        "2️⃣ Обязательно укажи свой @username в комментарии к платежу.\n"
        "3️⃣ После оплаты вернись и нажми кнопку \"✅ Я оплатил\".\n\n"
        "После проверки доната ты получишь доступ к закрытому контенту. Спасибо за поддержку!",
        reply_markup=reply_markup
    )

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Убедись, что указал @username и сумма не меньше $0.15.")

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200
