from core import get_service, get_content_from_google_sheets, get_exchange_rate, db_operations
from time import sleep
from config import BOT_API, BOT_NAME
import logging
from aiogram import Bot, Dispatcher, executor, types
import threading
from db import Database

# Telegram bot and db setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_API)
dp = Dispatcher(bot)
db = Database()

#приветствие
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.reply("Добро пожаловать!")


#ответ на любое сообщение
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("im alive")


def init():
    service = get_service()  # ресурс для работы с Google Sheets API
    while True:
        content = get_content_from_google_sheets(service)  # получение контента из GoogleSheets
        exchange_rate = get_exchange_rate()  # парсинг курса валют с ЦБ РФ
        db_operations(content, exchange_rate)  # операции с базой данных
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------")
        sleep(3)



if __name__ == '__main__':
    thread_1 = threading.Thread(name="Init", target=init)
    thread_1.start()
    executor.start_polling(dp, skip_updates=True)

