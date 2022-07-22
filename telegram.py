from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import BOT_API
import logging
from queue import Queue


# Telegram bot and db setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_API)
dp = Dispatcher(bot)
db = Database()


# приветствие
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.reply("Добро пожаловать!")


# ответ на любое сообщение
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Я еще живой")


async def send_telegram(order_numbers):
    print("TELEGRAM order_numbers", order_numbers)
    try:
        # print(q.empty())
        # if not q.empty():
        #     order_numbers = q.get()
        #     await bot.send_message(chat_id=1353223764, text=order_numbers)
        await bot.send_message(chat_id=1353223764, text=order_numbers)
    except Exception as _ex:
        print("[INFO] Error with telegram: ", _ex)


def start_polling():
    executor.start_polling(dp, skip_updates=True)
    return
