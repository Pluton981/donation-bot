import logging
import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Получаем токен из переменных окружения
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("❌ Переменная окружения 'TOKEN' не установлена!")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

donations = []
MIN_AMOUNT = 0.15
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DONATE_URL = "https://www.donationalerts.com/r/archive_unlock?v=2"

@app.route('/')
def home():
    return '✅ Бот работает'

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"💸 Новый донат: {username} — {amount} USD")
    return "OK", 200

def start(update, context):
    keyboard = [[InlineKeyboardButton("💳 ОПЛАТИТЬ", url=DONATE_URL)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    intro_text = (
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день."
    )

    update.message.reply_text(intro_text)

    with open("kaspi.jpg", "rb") as photo:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)

    main_text = (
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
        "1️⃣ Нажми [ОПЛАТИТЬ] и сделай перевод на $20\n"
        "2️⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
        "3️⃣ После оплаты нажми [✅ Я оплатил]\n"
        "4️⃣ Получи ссылку на материал"
    )

    update.message.reply_text(main_text, reply_markup=reply_markup)

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Укажи @username и сумму от $20.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
