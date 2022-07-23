from aiogram import Bot, Dispatcher, executor, types
from db import Database
from config import BOT_API
import logging
from datetime import datetime, date

# Telegram bot and db setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_API)
dp = Dispatcher(bot)
db = Database()


# отправка сообщения пользователю о просроченных заказах
async def send_telegram(notified_orders):
    not_notified_orders = db.check_notified_orders(notified_orders)
    if not_notified_orders != []:
        message = "Доброго времени суток!\nОбнаружены заказы с истекшим сроком поставки:\n"
        for i in not_notified_orders:
            message = message+"№"+str(i[1])+"; Стоимость, $: "+str(i[2])+"; Стоимость, руб.: "+str(i[3])+"; Срок поставки: "+i[4].strftime("%Y-%m-%d")+";\n"
        users = db.get_users()
        for i in users:
            await bot.send_message(i[0], message)


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
