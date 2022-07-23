from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import BOT_API
import logging


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


# async def send_telegram(order_numbers):
#     print("TELEGRAM order_numbers", order_numbers)
#     print(await bot.send_message(chat_id="1353223764", text=order_numbers))
#     await bot.send_message(chat_id="1353223764", text=order_numbers)


async def send_telegram(notified_orders):
    result = str(notified_orders)
    print("TELEGRAM")
    await bot.send_message("@MolokovKlim", result)


    print("====================================================MESSAGE DID NOT SENDED=======================================")


# sendall
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






# ответ на любое сообщение
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Я еще живой")

def start_polling():
    executor.start_polling(dp, skip_updates=True)
    return
