Skip to content
Chat history



Today
Yesterday
Previous 7 Days
Previous 30 Days
You said:
платежка для бота
ChatGPT said:
Привожу шаблон простой платежки (инструкции по оплате) для Telegram-бота, которую можно вставить в сообщение, когда пользователь нажимает кнопку "ОПЛАТИТЬ":

💳 Инструкция по оплате

Для активации доступа, отправьте донат от $0.15 (или в вашей валюте) по ссылке:

👉 [donationalerts.com/r/ВАШ_ЮЗЕРНЕЙМ](https://

You said:
в общем ты все забыл, мы уже сделали бот с платежкой в DA, но не смогли запустить автоматизацию, теперь предлагаю сервис youmoney, нужно чтобы пользователь увидел материал нажал ОПЛАТИТЬ, выполнил действия после этого нажал кнопку Я ОПЛАТИЛ и бот проверил транзакцию если она есть то выдал ссылку
ChatGPT said:
Memory updated
Отлично, с YouMoney можно реализовать этот процесс. Вот как будет работать логика:

🔁 Сценарий Telegram-бота с YouMoney
Показ материала → бот отправляет описание + прикреплённый скрин.

Кнопка "ОПЛАТИТЬ" → бот отправляет реквизиты (например: номер Kaspi, ссылка на оплату через YouMoney, QR-код и т.д.).

Пользователь переводит → нажимает кнопку "✅ Я оплатил".

Бот проверяет входящие переводы на YouMoney через API:

по сумме (минимум $0.15 или эквивалент),

по комментарию (например, username Telegram),

по времени (например, последние 10 минут).

Если платёж найден — бот выдаёт ссылку на материал или делает редирект.

Хочешь, чтобы я сразу переписал main.py под это? Нужно:

Твой API-ключ от YouMoney;

Какой параметр должен указывать пользователь (например, свой username в комментарии к переводу).

Готов?

You said:
да 
ChatGPT said:
Отлично! Тогда вот, что мне нужно от тебя:

🧾 Чтобы всё сразу заработало:
API-ключ YouMoney (можешь заменить его на your_api_key — я вставлю заглушку, ты потом подставишь настоящий).

Номер кошелька YouMoney (или ID, если используется OAuth).

Подтверждаем:

Пользователь будет в комментарии к переводу указывать свой username Telegram?

Минимальная сумма — $0.15 (можно сразу в тенге/рублях, если хочешь)?

Ссылка, которую бот должен выдать после успешной оплаты (Google Drive и т.д.).

Как только дашь это — я сразу перепишу main.py с кнопками и проверкой транзакции через API YouMoney.

You said:
а как найти api 
ChatGPT said:
Смотри, чтобы получить API-доступ к YouMoney (ex-ЮMoney, бывшая Яндекс.Деньги), нужно:

🔐 Как получить API-ключ YouMoney:
📌 1. Зарегистрируйся или войди:
Перейди на https://yoomoney.ru и войди в свой аккаунт.

📌 2. Перейди в раздел для разработчиков:
👉 https://yoomoney.ru/myservices/new

Это страница создания нового приложения, которое получает доступ к API.

📌 3. Заполни форму:
Название приложения: любое (например, Telegram Bot).

Описание: можешь указать Бот для проверки платежей.

Callback URL: можно пока вписать https://example.com — мы не используем его в нашем случае.

Redirect URI: тоже https://example.com (если не используем OAuth — не критично).

Выбери нужные права доступа:

account-info

operation-history

operation-details

📌 4. Сохрани и получи OAuth-токен:
После подтверждения тебе сгенерируют OAuth-токен — это и есть твой API-ключ.

‼️ Важно: при генерации тебя может перекинуть на ссылку вида

https://yoomoney.ru/oauth/authorize?response_type=token&client_id=ВАШ_ID&scope=...
Ты просто авторизуешься и получаешь токен в адресной строке браузера — он будет выглядеть так:

access_token=41001xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Скопируй его — это и есть ключ.

💡 Если хочешь, я могу пошагово провести тебя через весь процесс вживую. Только скажи.
А как получишь ключ — пиши сюда, я сразу вставлю в main.py.

You said:
Uploaded image
ChatGPT said:
Отлично, ты на правильной странице! Вот что нужно вписать, чтобы быстро пройти регистрацию:

✍️ Что ввести в поля:
Название для пользователей:
telegram donats — оставь, как есть.

Адрес сайта:
👉 Впиши что-то вроде http://example.com — этот параметр обязателен, но он не используется, если тебе не нужен редирект.

Почта для связи:
Впиши свою рабочую или любую активную почту.

Redirect URI:
Впиши тоже http://example.com.

Notification URI:
Можно тоже http://example.com или просто оставить пустым.

Логотип:
Необязательно загружать.

После отправки формы ты получишь client_id, а затем при авторизации — OAuth токен, который выглядит так:

41001xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🔐 Этот токен ты потом вставишь в код как access_token.

Когда получишь токен — скинь его (можно с маскировкой, я подставлю заглушку), и я сразу перепишу main.py под YouMoney.
Готов идти дальше?

You said:
06A3B002CB441ECF28EAFAF2446280A50094CF624E09C237138B7D653C37CE61
ChatGPT said:
Отлично! У нас теперь есть токен, я вставлю его как переменную YOUMONEY_TOKEN и напишу весь main.py с учётом следующей логики:

📲 Логика Telegram-бота:
Пользователь получает приветствие и материал (с изображением).

Кнопка "ОПЛАТИТЬ" → получает реквизиты.

Переводит деньги на кошелёк YouMoney (с username в комментарии).

Нажимает "✅ Я ОПЛАТИЛ".

Бот проверяет последние входящие переводы:

Минимум 0.15 USD;

В комментарии — его username.

Если совпало → бот выдаёт ссылку (например, на Google Drive).

Сейчас напишу и скину готовый main.py.

Вот готовый main.py, переписанный под YouMoney:

import os
import time
import requests
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
YOUMONEY_TOKEN = "06A3B002CB441ECF28EAFAF2446280A50094CF624E09C237138B7D653C37CE61"
YOUMONEY_API = "https://yoomoney.ru/api/operation-history"
MIN_AMOUNT = 0.15  # минимальная сумма в USD
MATERIAL_LINK = "https://your-google-drive-link.com"  # ссылка на материал

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Кнопки
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 ОПЛАТИТЬ", callback_data='pay')],
        [InlineKeyboardButton("✅ Я ОПЛАТИЛ", callback_data='check_payment')]
    ])

# Команда /start
def start(update, context):
    username = update.effective_user.username or "без username"
    text = f"""🔥 Материал: AI-девушка 2.0

При трудозатратах ~30 мин в день.

Вложение: <b>от $0.15</b> через YouMoney. 
В комментарии к переводу укажите ваш username: <code>{username}</code>.

После оплаты нажмите кнопку "✅ Я ОПЛАТИЛ".
"""
    with open("kaspi.jpg", "rb") as photo:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=text, parse_mode="HTML", reply_markup=get_main_keyboard())

# Обработка кнопок
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or ""

    if query.data == "pay":
        text = f"""💳 Переведите от $0.15 на YouMoney:

👉 Номер: <code>41001123456789</code>  
❗️В комментарии укажите ваш username: <b>{username}</b>  

После оплаты нажмите "✅ Я ОПЛАТИЛ"
"""
        bot.send_message(chat_id=user_id, text=text, parse_mode="HTML", reply_markup=get_main_keyboard())

    elif query.data == "check_payment":
        if check_yoomoney_payment(username):
            bot.send_message(chat_id=user_id, text="✅ Платёж найден! Вот ваша ссылка:\n" + MATERIAL_LINK)
        else:
            bot.send_message(chat_id=user_id, text="❌ Платёж не найден. Убедитесь, что указали username в комментарии и сумма не ниже $0.15.")

# Проверка платежей YouMoney
def check_yoomoney_payment(username):
    headers = {"Authorization": f"Bearer {YOUMONEY_TOKEN}"}
    data = {
        "type": "deposition",
        "records": 20,
    }

    response = requests.post(YOUMONEY_API, headers=headers, data=data)
    if response.status_code != 200:
        return False

    operations = response.json().get("operations", [])
    now = time.time()

    for op in operations:
        if (
            float(op.get("amount", 0)) >= MIN_AMOUNT
            and username.lower() in (op.get("message", "")).lower()
            and abs(now - parse_time(op.get("datetime", ""))) < 900  # последние 15 минут
        ):
            return True
    return False

def parse_time(iso_time_str):
    from datetime import datetime
    dt = datetime.fromisoformat(iso_time_str.replace("Z", "+00:00"))
    return dt.timestamp()

# Flask хук
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    dispatcher.process_update(telegram.Update.de_json(update, bot))
    return "ok"

# Установка хендлеров
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# Запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
📌 Что тебе нужно сделать:
Заменить:

YOUR_TELEGRAM_BOT_TOKEN — на токен бота;

41001123456789 — на номер твоего кошелька YouMoney;

https://your-google-drive-link.com — на ссылку на материал;

Подгрузить файл kaspi.jpg в ту же папку.

Задеплой на Render или любой сервер, как раньше.

Хочешь, чтобы я ещё добавил лог отправки (для логов в файл) или ограничение по одному доступу на username?

You said:
Uploaded image
мы отказались от фласка я скину тебе актуальный main.py
ChatGPT said:
Отлично, понял — Flask больше не используем. Жду от тебя актуальный main.py, чтобы адаптировать его под YouMoney и встроить проверку платежей после кнопки "✅ Я ОПЛАТИЛ".

Когда будешь готов — скинь файл, я перепишу весь код под новую логику с сохранением всех кнопок и функций.

You said:
import logging
import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TOKEN")
DA_SECRET = os.environ.get("DA_SECRET")

if not TELEGRAM_TOKEN or not DA_SECRET:
    raise ValueError("❌ Отсутствует TELEGRAM TOKEN или DA SECRET")

# Настройка
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
logging.basicConfig(level=logging.INFO)

# Данные
donations = []
MIN_AMOUNT = 0.15
CONTENT_LINK = "https://drive.google.com/drive/folders/18OEeQ4QhgHEDWac1RJz0PY8EoJVZbGH_?usp=drive_link"
DA_EXPECTED_CURRENCY = "USD"

@app.route("/")
def home():
    return "✅ Бот работает!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    headers = request.headers

    if headers.get("Authorization") != f"Bearer {DA_SECRET}":
        return "Unauthorized", 403

    if data and 'username' in data and 'amount' in data:
        username = data['username'].lstrip('@').lower()
        amount = float(data['amount'])
        currency = data.get("currency", "").upper()

        if currency == DA_EXPECTED_CURRENCY:
            donations.append({'username': username, 'amount': amount})
            logging.info(f"💸 Новый донат: {username} — {amount} {currency}")

    return "OK", 200

def start(update, context):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", url="https://www.donationalerts.com/r/archive_unlock?v=2")],
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

def check_payment(update, context):
    query = update.callback_query
    user = query.from_user
    username = user.username.lower() if user.username else ""

    for donation in donations:
        if username in donation['username'] and donation['amount'] >= MIN_AMOUNT:
            query.message.reply_text(f"🎉 Спасибо! Вот ссылка: {CONTENT_LINK}")
            return

    query.message.reply_text("❌ Донат не найден. Укажи @username и сумму от $0.15.")

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

def clear_donations():
    donations.clear()
    logging.info("🧹 Донаты очищены")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(clear_donations, "interval", hours=12)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
ChatGPT said:
Memory updated
Отлично! Теперь перепишу твой main.py под YouMoney, убрав логику с DonationAlerts (DA_SECRET и т.д.) и заменив её на проверку транзакций через YouMoney API.

🔧 Что изменится:
Удалим /webhook и связанные с ним вещи.

Вместо donations[] бот будет обращаться к API YouMoney при нажатии на "✅ Я оплатил".

Username будет сравниваться с комментарием к переводу.

Валюта — USD, минимальная сумма — $0.15.

Сейчас перепишу и пришлю готовый main.py.

Вот обновлённый main.py, полностью адаптированный под YouMoney (вместо DonationAlerts):

import logging
import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from datetime import datetime

# Токены и ключи
TELEGRAM_TOKEN = os.environ.get("TOKEN")
YOUMONEY_TOKEN = os.environ.get("YOUMONEY_TOKEN")  # теперь ключ от YouMoney

if not TELEGRAM_TOKEN or not YOUMONEY_TOKEN:
    raise ValueError("❌ Отсутствует TELEGRAM_TOKEN или YOUMONEY_TOKEN")

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
        [InlineKeyboardButton("💵 ОПЛАТИТЬ", url="https://yoomoney.ru/to/41001123456789")],  # замени на свой кошелёк
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
            abs(now - time_ts) < 900  # последние 15 минут
        ):
            return True

    return False

def parse_iso_to_ts(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.timestamp()

# Плановое очищение (если нужно)
def dummy():
    logging.info("🧹 Плановая задача")

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(dummy, "interval", hours=12)
scheduler.start()

# Обработчики
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(check_payment))
🟡 Что тебе нужно сделать:
В .env или Render переменных окружения:

TOKEN — токен Telegram-бота;

YOUMONEY_TOKEN — токен от YouMoney (который ты уже получил).

Замени ссылку в InlineKeyboardButton("💵 ОПЛАТИТЬ", url="...") на свою:

https://yoomoney.ru/to/ТВОЙ_НОМЕР_КОШЕЛЬКА
Убедись, что kaspi.jpg лежит в одной папке с main.py.

Залей на Render как раньше, у тебя уже всё настроено.

Хочешь, чтобы бот отправлял сообщение, если пользователь уже получал доступ ранее (по памяти)?








ChatGPT can make mistakes. Check important info.
?
