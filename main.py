from core import get_service, get_content_from_google_sheets, get_exchange_rate, db_operations
from telegram import start_polling
import asyncio



async def init():
    service = get_service()  # ресурс для работы с Google Sheets API
    while True:
        content = get_content_from_google_sheets(service)  # получение контента из GoogleSheets
        exchange_rate = get_exchange_rate()  # парсинг курса валют с ЦБ РФ
        db_operations(content, exchange_rate)  # операции с базой данных
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------")
        await asyncio.sleep(3)


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(init()) #run init() in background
    start_polling()
    print("after polling")


