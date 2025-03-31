import os
import logging
from flask import Flask, request
from telegram import Bot, Update, InputMediaPhoto
from telegram.ext import CommandHandler, Dispatcher
from telegram.utils.request import Request
from threading import Thread

TOKEN = os.environ.get("TOKEN")
DA_SECRET = os.environ.get("DA_SECRET")

if not TOKEN or not DA_SECRET:
    raise ValueError("❌ Отсутствует TELEGRAM TOKEN или DA TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# Хранилище chat_id по username
user_data = {}

@app.route('/')
def home():
    return '✅ Бот работает'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    username = data.get("username", "").lower().replace("@", "")
    amount = data.get("amount")

    logging.info(f"💸 Новый донат: {username} — {amount} USD")

    if username in user_data:
        chat_id = user_data[username]
        bot.send_message(chat_id=chat_id, text="🎉 Спасибо за поддержку! Вот твой контент: https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link")
    else:
        logging.warning(f"❗ Не найден пользователь с username @{username}")

    return 'ok'

def start(update: Update, context):
    username = update.message.from_user.username.lower()
    chat_id = update.message.chat_id
    user_data[username] = chat_id

    with open("kaspi.jpg", "rb") as photo:
        context.bot.send_photo(chat_id=chat_id, photo=photo)

    context.bot.send_message(
        chat_id=chat_id,
        text=(
            "💸 Вывод за неделю — $1 250\n"
            "Без лица.\n"
            "Без публичности.\n"
            "При трудозатратах ~30 мин в день.\n\n"
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
            "1️⃣ Нажми [ОПЛАТИТЬ](https://www.donationalerts.com/r/archive_unlock?v=2) и сделай перевод на $20\n"
            "2️⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
            "3️⃣ После оплаты нажми [✅ Я оплатил]\n"
            "4️⃣ Получи ссылку на материал"
        ),
        parse_mode='Markdown'
    )

dispatcher.add_handler(CommandHandler("start", start))

def run_telegram():
    from telegram.ext import Updater
    updater = Updater(token=TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()

Thread(target=run_telegram).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
