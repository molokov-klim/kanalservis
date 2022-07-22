from core import get_service, get_content_from_google_sheets, get_exchange_rate, db_operations
from time import sleep
import threading
from telegram import start_polling

import asyncio


# from queue import Queue
#
# q = queue.Queue()

def init(loop):
    service = get_service()  # ресурс для работы с Google Sheets API
    while True:
        content = get_content_from_google_sheets(service)  # получение контента из GoogleSheets
        exchange_rate = get_exchange_rate()  # парсинг курса валют с ЦБ РФ
        db_operations(content, exchange_rate, loop)  # операции с базой данных
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------")
        sleep(3)


if __name__ == '__main__':
    # q = Queue()
    loop = asyncio.new_event_loop()

    thread_1 = threading.Thread(name="Init", target=init, args=(loop,))
    thread_1.start()
    start_polling()
    print("after polling")


