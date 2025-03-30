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

# Настройка Flask и Telegram Bot
app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Донаты (временное хранилище)
donations = []

# Настройки
MIN_AMOUNT = 0.15
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DA_LINK = "https://www.donationalerts.com/r/archive_unlock?v=2"

@app.route('/')
def home():
    return '✅ Бот успешно работает!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'username' in data and 'amount' in data:
        username = data['username']
        amount = float(data['amount'])
        donations.append({'username': username.lower(), 'amount': amount})
        logging.info(f"💸 Новый донат: {username} — {amount} USD")
    return "OK", 200

def start(update, context):
    keyboard = [[InlineKeyboardButton("💵 ОПЛАТИТЬ", url=DA_LINK)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Текст до изображения
    text_top = (
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день."
    )

    # Текст после изображения
    text_bottom = (
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

    update.message.reply_text(text_top)

    # Отправим изображение выплат
    with open("photo_2025-03-31_03-23-57 копия.jpg", "rb") as photo:
        update.message.reply_photo(photo)

    update.message.reply_text(text_bottom, reply_markup=reply_markup)

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо за поддержку! Вот твой контент:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Убедись, что указал @username и сумму не меньше $20.")

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
