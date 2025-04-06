
import logging
import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from datetime import datetime

# Токены
TELEGRAM_TOKEN = "7322072186:AAF8rbIQ8P_B11vLx2QNOM9-Rnblo6mf7hc"
YOUMONEY_TOKEN = "06A3B002CB441ECF28EAFAF2446280A50094CF624E09C237138B7D653C37CE61"

# Настройка
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Данные
MIN_AMOUNT = 0.15
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"

@app.route("/")
def home():
    return "✅ Бот работает!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Старт
def start(update, context):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", url="https://yoomoney.ru/to/4100116270792125")],
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

# Обработка кнопки "✅ Я оплатил"
def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    if not username:
        query.message.reply_text("❌ У вас не установлен username. Установите его в настройках Telegram и попробуйте снова.")
        return

    if verify_yoomoney_payment(username):
        query.message.reply_text(f"🎉 Спасибо! Вот ссылка на материал:\n{CONTENT_LINK}")
    else:
        query.message.reply_text("❌ Донат не найден. Убедитесь, что перевели от $0.15 и указали @username в комментарии.")

# Проверка YouMoney
def verify_yoomoney_payment(username):
    headers = {"Authorization": f"Bearer {YOUMONEY_TOKEN}"}
    data = {
        "type": "deposition",
        "records": 25
    }

    response = requests.post("https://yoomoney.ru/api/operation-history", headers=headers, data=data)
    if response.status_code != 200:
        logging.warning("Не удалось получить историю операций")
        return False

    operations = response.json().get("operations", [])
    now = datetime.utcnow().timestamp()

    for op in operations:
        amount = float(op.get("amount", 0))
        message = op.get("message", "").lower()
        time_str = op.get("datetime", "")
        time_ts = parse_iso_to_ts(time_str)

        if (
            username in message and
            amount >= MIN_AMOUNT and
            abs(now - time_ts) < 900
        ):
            return True

    return False

def parse_iso_to_ts(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.timestamp()

# Плановая задача (опционально)
def dummy():
    logging.info("🧹 Плановая задача")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(dummy, "interval", hours=12)
scheduler.start()

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

# Обязательный запуск с портом от Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
