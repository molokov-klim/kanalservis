from datetime import datetime, date
import psycopg2
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, HOST, PORT, USER, PASSWORD, DB_NAME
from telegram import send_telegram
import requests


# создает ресурс для работы с Google Sheets API
def get_service():
    creds_json = os.path.dirname(
        __file__) + "/creds/kanalservis_key.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


# получение контента из GoogleSheets
def get_content_from_google_sheets(service):
    sheet = service.spreadsheets()
    content = sheet.values().batchGet(spreadsheetId=SHEET_ID, ranges=["Лист1"]).execute()
    content = content['valueRanges'][0]['values']
    content.pop(0)
    return content


# парсинг курса валют с ЦБ РФ
def get_exchange_rate():
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return exchange_rate['Valute']['USD']['Value']


# операции с базой данных
def db_operations(content, exchange_rate):
    try:
        connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        with connection.cursor() as cursor:
            cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", ('orders',))
            isExist = cursor.fetchone()[0]
            if isExist:
                #notified_orders = check_dates(cursor)
                #print("notified_orders")                            ####
                #print(notified_orders)                              ####
                content = convert_date(content)



            # получаю гугл таблицу
            # получаю курс валют
            # проверяю есть ли таблица (формальная проверка, она должна быть)
            # иду в базу, проверяю даты
            #   если дата устарела,то проверяю дату уведомления, если сегодня или 3333 то пропуск, если прошла, то отправляю уведомление в ТГ
            #   формирую тупл order_number, если notif_date = сегодня
            # привожу таблицу к добавлению в бд:
            #   меняю формат даты
            #   добавляю сумму в рублях
            #   добавляю notif_date 3333 г. если нет совпадения по order_number. если сопадение есть то дата = сегодня
            #   преобразую в тюпл тюплов
            # truncate
            # формирую запрос для инсерта
            # insert
            #
            #
            #
            #










    except Exception as _ex:
        print("[INFO] Error while working with PostrgeSQL ", _ex)

    finally:
        if connection:
            connection.close()


# проверка дат уведомлений в БД. возвращает список заказов с сегодняшней датой уведомления
def check_dates(cursor):
    cursor.execute("select * from orders")
    orders = cursor.fetchall()
    for i in orders:
        print(i)

 # иду в базу, проверяю даты
            #   если дата устарела,то проверяю дату уведомления, если сегодня или 3333 то пропуск, если прошла, то отправляю уведомление в ТГ
            #   формирую тупл order_number, если notif_date = сегодня

# конвертация даты
def convert_date(content):
    print("content before")
    print(content)
    for i in content:
        date_str = i[3]
        formatter_string = "%d.%m.%Y"
        datetime_object = datetime.strptime(date_str, formatter_string)
        i[3] = str(datetime_object.date())
    print("content after")
    print(content)

    # date_str = element[4]
    # formatter_string = "%d.%m.%Y"
    # datetime_object = datetime.strptime(date_str, formatter_string)
    # if(datetime_object.date()<date.today()):
    #      current_date = str(date.today())
    #      element[5] = current_date
    # element[4] = str(datetime_object.date())
    # return element

