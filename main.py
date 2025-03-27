import logging
import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("❌ Переменная окружения 'TOKEN' не установлена!")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

donations = []
MIN_AMOUNT = 0.15  # в долларах для теста
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DONATE_LINK = "https://www.donationalerts.com/r/archive_unlock?v=2"

@app.route('/')
def home():
    return '✅ Бот работает!'

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"💸 Новый донат: {username} — {amount}$")
    return "OK", 200

def start(update, context):
    keyboard = [[InlineKeyboardButton("💸 ОПЛАТИТЬ", url=DONATE_LINK)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Привет! 🎉\n\n"
        "Чтобы получить доступ к приватному материалу, выполни следующие шаги:\n\n"
        "1️⃣ Перейди по кнопке 'ОПЛАТИТЬ' и сделай донат от 0.15$ (USD).\n"
        "2️⃣ ОБЯЗАТЕЛЬНО укажи свой @username в комментарии к донату!\n"
        "3️⃣ Нажми кнопку '✅ Я оплатил' после завершения оплаты.\n\n"
        "После проверки доната ты получишь ссылку на материал.\n",
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

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
