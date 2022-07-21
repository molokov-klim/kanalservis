from core_new import get_service, get_content_from_google_sheets, get_exchange_rate, db_operations
from time import sleep


def init():
    service = get_service() # ресурс для работы с Google Sheets API
    while True:
        sleep(0)
        content = get_content_from_google_sheets(service) # получение контента из GoogleSheets
        exchange_rate = get_exchange_rate() # парсинг курса валют с ЦБ РФ
        db_operations(content, exchange_rate) #операции с базой данных



if __name__ == '__main__':
    init()








