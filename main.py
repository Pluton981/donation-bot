
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
QIWI_TOKEN = "bc03ddff40973afe4bad801342fb7e9f"
QIWI_PHONE = "77786808870"

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
        [InlineKeyboardButton("💵 ОПЛАТИТЬ (QIWI)", url="https://qiwi.com/payment/form/99?extra%5B%27account%27%5D=77786808870&amountInteger=1&currency=398&comment=@username")],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "💸 Минимальный донат: от $0.15 (≈ 70–150₸)
"
        "Оплата доступна с карты любого банка через QIWI.
"
        "❗ В комментарии обязательно укажи свой @username из Telegram."
    )
    update.message.reply_text(message)

    with open("kaspi.jpg", "rb") as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)

    instructions = (
        "\n1⃣ Нажми [ОПЛАТИТЬ] и сделай перевод
"
        "2⃣ Укажи @username в комментарии
"
        "3⃣ Нажми [✅ Я оплатил]
"
        "4⃣ Получи ссылку на материал"
    )
    update.message.reply_text(instructions, reply_markup=reply_markup)

# Обработка кнопки "✅ Я оплатил"
def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    if not username:
        query.message.reply_text("❌ У вас не установлен username. Установите его в настройках Telegram и попробуйте снова.")
        return

    if verify_qiwi_payment(username):
        query.message.reply_text(f"🎉 Спасибо! Вот ссылка на материал:\n{CONTENT_LINK}")
    else:
        query.message.reply_text("❌ Донат не найден. Убедитесь, что вы указали @username в комментарии и сумма не менее $0.15.")

# Проверка платежей QIWI
def verify_qiwi_payment(username):
    url = f"https://edge.qiwi.com/payment-history/v2/persons/{QIWI_PHONE}/payments"
    headers = {
        "Authorization": f"Bearer {QIWI_TOKEN}"
    }
    params = {
        "rows": 20,
        "operation": "IN"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            logging.warning("⚠️ Не удалось получить историю QIWI")
            return False

        data = response.json()
        now = datetime.utcnow().timestamp()

        for tx in data.get("data", []):
            amount = tx.get("sum", {}).get("amount", 0)
            comment = tx.get("comment", "") or ""
            date_str = tx.get("date", "")
            tx_ts = parse_iso_to_ts(date_str)

            if (
                username in comment.lower() and
                float(amount) >= MIN_AMOUNT and
                abs(now - tx_ts) < 900
            ):
                return True

    except Exception as e:
        logging.error(f"❌ Ошибка при запросе QIWI API: {e}")
    return False

def parse_iso_to_ts(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.timestamp()

# Плановая задача
def dummy():
    logging.info("🧹 Плановая задача")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(dummy, "interval", hours=12)
scheduler.start()

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
