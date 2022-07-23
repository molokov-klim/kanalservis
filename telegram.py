from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import BOT_API
import logging

# Telegram bot and db setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_API)
dp = Dispatcher(bot)
db = Database()


# корутина вызывается, принимает нужные аргументы, send.message отрабатывает без ошибок и возвращает return,
# но сообщение в телеграм не приходит
async def send_telegram(notified_orders):
    result = str(notified_orders)
    print("[TELEGRAM] Received args (notified_orders) :", notified_orders)
    await bot.send_message("@MolokovKlim", result)


# хэндлер приветствия
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.reply("Добро пожаловать!")


# хендлер ответ на любое сообщение
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Я здесь")


# DEBUG ONLY
@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.chat.type == 'private':
        text = message.text[9:]
        users = db.get_users()
        for row in users:
            try:
                await bot.send_message(row[0], text)
                if int(row[1]) != 1:
                    db.set_active(row[0], 1)
            except:
                db.set_active(row[0], 0)
        print("message.from_user.id ", message.from_user.id)
        await bot.send_message(message.from_user.id, "Успешная рассылка")


def start_polling():
    executor.start_polling(dp, skip_updates=True)
    return
