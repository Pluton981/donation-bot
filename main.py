import logging
import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Получаем токен из переменных окружения
TOKEN = os.environ.get("TOKEN")

# Проверка: если токен не найден — логируем ошибку
if not TOKEN:
    raise ValueError("❌ Переменная окружения 'TOKEN' не установлена!")

# Настройка бота и Flask
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Хранилище донатов
donations = []

# Настройки
MIN_AMOUNT = 300
CONTENT_LINK = "https://telegra.ph/Ayazhan-Secret-File-03-27"

# Главная страница
@app.route('/')
def home():
    return '✅ Бот успешно работает!'

# Обработка доната с donationalerts
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"💸 Новый донат: {username} — {amount}₽")
    return "OK", 200

# Команда /start
def start(update, context):
    keyboard = [[InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Сделай донат от 300₽ сюда:\nhttps://www.donationalerts.com/r/archive_unlock\n\n"
        "⚠️ Обязательно укажи свой @username в комментарии к донату!",
        reply_markup=reply_markup
    )

# Обработка кнопки "Я оплатил"
def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Убедись, что указал @username и сумма не меньше 300₽.")

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

# Webhook от Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Запуск приложения с портом от Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
