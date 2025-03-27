import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
import threading

TOKEN ="7322072186:AAF8rbIQ8P_B11vLx2QNOM9-Rnblo6mf7hc"
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Хранилище донатов
donations = []

MIN_AMOUNT = 300  # минимальная сумма
CONTENT_LINK = "https://telegra.ph/Ayazhan-Secret-File-03-27"  # замени на свой
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
    keyboard = [[
        InlineKeyboardButton("Я оплатил", callback_data="check_payment")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Сделай донат на сумму от 300₽ сюда: https://www.donationalerts.com/r/archive_unlock\n\n"
        "⚠️ В комментарии к донату обязательно укажи свой @username, чтобы я могла тебя узнать!",
        reply_markup=reply_markup)


def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation[
                'amount'] >= MIN_AMOUNT:
            query.message.reply_text(
                f"Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")

            return
    query.message.reply_text(
        "❌ Донат не найден. Убедись, что указал @username в комментарии и сумма не ниже 300₽."
    )


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))


@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200


def run():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    threading.Thread(target=run).start()
    print("Бот запущен.")
