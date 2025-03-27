import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
import os

TOKEN = os.environ.get("TOKEN")  # Получаем токен из переменных окружения
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

donations = []
MIN_AMOUNT = 300
CONTENT_LINK = "https://telegra.ph/Ayazhan-Secret-File-03-27"

@app.route('/')
def home():
    return 'Бот успешно работает!'

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"New donation: {username} - {amount}")
    return "OK", 200

def start(update, context):
    keyboard = [[InlineKeyboardButton("Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Сделай донат от 300₽ сюда: https://www.donationalerts.com/r/archive_unlock\n\n"
        "⚠️ Укажи свой @username в комментарии!",
        reply_markup=reply_markup
    )

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Укажи @username и сумму от 300₽.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200
