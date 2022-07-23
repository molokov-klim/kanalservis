from core import get_service, get_content_from_google_sheets, get_exchange_rate, db_operations
from telegram import start_polling
import asyncio
from datetime import datetime


async def init():
    service = get_service()  # ресурс для работы с Google Sheets API
    while True:
        print(f"[INFO] Server time {datetime.now()}")
        content = get_content_from_google_sheets(service)  # получение контента из GoogleSheets
        exchange_rate = get_exchange_rate()  # парсинг курса валют с ЦБ РФ
        await db_operations(content, exchange_rate)  # операции с базой данных
        await asyncio.sleep(3)


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(init())  # run init() in background
    start_polling()  # run polling in main thread
