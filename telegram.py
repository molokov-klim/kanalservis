from config import BOT_API, BOT_NAME
import logging
from aiogram import Bot, Dispatcher, executor, types

def send_telegram(row):
    print('telegram')
    print(row)
    pos = str(row[0])
    order_number = str(row[1])
    price_usd = str(row[2])
    price_rub = str(row[3])
    delivery_date = str(row[4])





