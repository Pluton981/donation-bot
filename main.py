import logging
import os
import uuid
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from datetime import datetime
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler

TELEGRAM_TOKEN = os.environ.get("TOKEN")
LAVA_JWT = os.environ.get("LAVA_JWT")
YOUMONEY_URL = "https://yoomoney.ru/to/4100116270792125"
LAVA_API_URL = "https://api.lava.kz/invoice/create"
DRIVE_LINK = "https://drive.google.com/drive/folders/1Bv8vEMKYJq2N-MojB--UVdj5ihrSrWm9?usp=sharing"

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

invoices = {}  # user_id: lava_invoice_id

def start(update, context):
    user = update.message.from_user

    first_text = (
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день."
    )
    update.message.reply_text(first_text)

    with open("kaspi.jpg", "rb") as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)

    after_image = (
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
        "🌟 Чтобы получить доступ:\n"
        "Закрытый доступ к инструкции — $0.15\n\n"
        "1⃣ Нажми [ОПЛАТИТЬ] и сделай перевод\n"
        "2⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
        "3⃣ После оплаты нажми ✅ [я оплатил]\n"
        "4⃣ Получи ссылку на материал"
    )

    keyboard = [
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", callback_data="choose_country")],
        [InlineKeyboardButton("✅ я оплатил", callback_data="check_payment")],
    ]
    update.message.reply_text(after_image, reply_markup=InlineKeyboardMarkup(keyboard))

def choose_country(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Россия", callback_data="pay_russia")],
        [InlineKeyboardButton("🇰🇿 Казахстан", callback_data="pay_kazakhstan")],
    ]
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

def create_lava_invoice(user_id, username):
    order_id = str(uuid.uuid4())
    invoices[user_id] = order_id
    payload = {
        "amount": 70,
        "order_id": order_id,
        "comment": username or "anon",
        "hook_url": "https://your-domain.com/lava_webhook",
        "success_url": "https://t.me/your_bot_username"
    }
    headers = {"Authorization": f"Bearer {LAVA_JWT}"}
    response = requests.post(LAVA_API_URL, json=payload, headers=headers)
    data = response.json()
    return data.get("url")

def handle_country(update, context):
    query = update.callback_query
    user = query.from_user

    if query.data == "pay_russia":
        query.edit_message_text("Перейди по ссылке для оплаты:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ЮMoney", url=YOUMONEY_URL)]
        ]))

    elif query.data == "pay_kazakhstan":
        invoice_url = create_lava_invoice(user.id, user.username)
        if invoice_url:
            query.edit_message_text("Перейди по ссылке для оплаты:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Оплатить через Lava", url=invoice_url)]
            ]))
        else:
            query.edit_message_text("Ошибка при создании счёта. Попробуйте позже.")

def check_payment(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in invoices:
        query.message.reply_text(f"🎉 Спасибо! Вот ссылка: {DRIVE_LINK}")
    else:
        query.message.reply_text("❌ Платёж не найден. Попробуйте позже.")

@app.route("/lava_webhook", methods=["POST"])
def lava_webhook():
    data = request.json
    logging.info(f"Webhook: {data}")

    if data.get("status") == "success":
        order_id = data.get("order_id")
        for uid, oid in invoices.items():
            if oid == order_id:
                bot.send_message(chat_id=uid, text=f"🎉 Спасибо! Вот ссылка: {DRIVE_LINK}")
                break
    return "OK", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(choose_country, pattern="^choose_country$"))
dispatcher.add_handler(CallbackQueryHandler(handle_country, pattern="^pay_"))
dispatcher.add_handler(CallbackQueryHandler(check_payment, pattern="^check_payment$"))

# Cron job to clear old invoices
scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(lambda: invoices.clear(), "interval", hours=6)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
