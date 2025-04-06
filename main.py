import os
import uuid
import logging
from flask import Flask, request
from telegram import (
    Bot, Update,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

# Токены
TELEGRAM_TOKEN = os.environ.get("TOKEN")
LAVA_JWT = os.environ.get("LAVA_JWT")
CONTENT_LINK = "https://drive.google.com/drive/folders/1Bv8vEMKYJq2N-MojB--UVdj5ihrSrWm9?usp=sharing"

# Настройка
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Хранилище
invoices = {}
MIN_AMOUNT = 0.15

@app.route("/")
def home():
    return "✅ Бот работает!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/lava_webhook", methods=["POST"])
def lava_webhook():
    data = request.json
    headers = request.headers
    order_id = data.get("order_id")
    status = data.get("status")

    logging.info(f"🌋 Webhook: {data}")

    if status == "success" and order_id in invoices:
        user_id = invoices[order_id]
        bot.send_message(chat_id=user_id, text=f"🎉 Спасибо! Вот ссылка на материал:\n{CONTENT_LINK}")
        del invoices[order_id]

    return "OK", 200

# /start
def start(update, context):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", callback_data="pay_select")],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "💸 Вывод за неделю — $1 250\n"
        "Без лица.\n"
        "Без публичности.\n"
        "При трудозатратах ~30 мин в день."
    )

    with open("kaspi.jpg", "rb") as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=reply_markup,
        text=(
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
            "💸 Чтобы получить доступ:\n"
            "Закрытый доступ к инструкции — $0.15\n\n"
            "1⃣ Нажми [ОПЛАТИТЬ] и сделай перевод\n"
            "2⃣ В комментарии ОБЯЗАТЕЛЬНО укажи свой @username в Телеграме\n"
            "3⃣ После оплаты нажми [✅ я оплатил]\n"
            "4⃣ Получи ссылку на материал"
        )
    )

# Обработка кнопок
def handle_button(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data == "pay_select":
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Россия (ЮMoney)", url="https://yoomoney.ru/to/4100116270792125")],
            [InlineKeyboardButton("🇰🇿 Казахстан (Lava)", callback_data="pay_lava")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
        ]
        query.message.reply_text("Выбери страну для оплаты:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "pay_lava":
        order_id = str(uuid.uuid4())
        invoices[order_id] = user.id

        import requests
        response = requests.post(
            "https://api.lava.kz/invoice/create",
            json={
                "amount": "70",  # В тенге
                "order_id": order_id,
                "comment": f"@{user.username or 'no_username'}",
                "custom_fields": {}
            },
            headers={"Authorization": f"Bearer {LAVA_JWT}"}
        )

        pay_url = response.json().get("data", {}).get("url")
        if pay_url:
            bot.send_message(chat_id=user.id, text=f"🔗 Ваша ссылка на оплату (KZ):\n{pay_url}")
        else:
            bot.send_message(chat_id=user.id, text="❌ Не удалось создать счёт через Lava. Попробуй позже.")

    elif data == "check_payment":
        bot.send_message(chat_id=user.id, text="⏳ Ожидаем подтверждение платежа...\nЕсли ты точно оплатил — оно скоро прилетит.\n\nЕсли не приходит — напиши вручную.")

    elif data == "back_main":
        start(update, context)

# Очистка
def clear_invoices():
    invoices.clear()
    logging.info("🧹 Очищены ожидающие счета")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(clear_invoices, "interval", hours=6)
scheduler.start()

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_button))
