import logging
import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TELEGRAM_TOKEN = os.environ.get("TOKEN")
DA_SECRET = os.environ.get("DA_SECRET")

if not TELEGRAM_TOKEN or not DA_SECRET:
    raise ValueError("❌ Отсутствует TELEGRAM TOKEN или DA TOKEN")

# Константы
DONATE_LINK = "https://www.donationalerts.com/r/archive_unlock?v=2"
KASPI_IMAGE = "kaspi.jpg"
MIN_AMOUNT = 0.15  # Минимальный донат в долларах
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"

# Инициализация Flask и Telegram
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Хранилище донатов
donations = []

# Главная страница
@app.route('/')
def index():
    return '✅ Бот успешно работает!'

# Webhook от DonationAlerts
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        username = data.get("username", "").lower().replace("@", "")
        amount = float(data.get("amount", 0))
        currency = data.get("currency", "RUB")

        # Преобразуем в USD по текущему курсу (если нужно)
        if currency == "RUB":
            try:
                rate = requests.get("https://api.exchangerate.host/latest?base=RUB&symbols=USD").json()["rates"]["USD"]
                amount *= rate
            except Exception as e:
                logger.warning(f"Ошибка получения курса: {e}")
                return "Exchange error", 500

        donations.append({"username": username, "amount": amount})
        logger.info(f"💸 Новый донат: {username} — {amount:.2f} USD")

    return "OK", 200

# Обработка команды /start
def start(update, context):
    user = update.message.from_user
    username = user.username or "друг"

    title = f"👋 Привет, @{username}!\n\n"
    part1 = (
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день.\n"
    )
    part2 = (
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
        "💵 Чтобы получить доступ:\n"
        "Закрытый доступ к инструкции — $20\n\n"
        "1️⃣ Нажми [ОПЛАТИТЬ] и сделай перевод на $20\n"
        "2️⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
        "3️⃣ После оплаты нажми [✅ Я оплатил]\n"
        "4️⃣ Получи ссылку на материал"
    )

    keyboard = [
        [InlineKeyboardButton("💸 ОПЛАТИТЬ", url=DONATE_LINK)],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(title + part1)

    # Отправка скрина
    try:
        with open(KASPI_IMAGE, 'rb') as photo:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    except Exception as e:
        logger.error(f"Ошибка при отправке скрина: {e}")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=part2,
        reply_markup=reply_markup
    )

# Проверка доната
def check_payment(update, context):
    query = update.callback_query
    username = (query.from_user.username or "").lower().replace("@", "")

    for donation in donations:
        if username in donation["username"] and donation["amount"] >= MIN_AMOUNT:
            query.message.reply_text(f"✅ Спасибо за поддержку! Вот твой материал:\n{CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Убедись, что указал свой @username в комментарии и сумма от $0.15.")

# Добавление обработчиков
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

# Webhook от Telegram
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Автосброс донатов (по желанию)
def clear_donations():
    donations.clear()
    logger.info("🧹 Список донатов очищен")

# Планировщик
scheduler = BackgroundScheduler()
scheduler.add_job(clear_donations, "interval", hours=12)
scheduler.start()

# Запуск Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
