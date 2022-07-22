from datetime import datetime, date
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import telegram
from config import SHEET_ID
import requests
from db import Database
from telegram import send_telegram
import asyncio

# Database setup
db = Database()

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
        if db.is_exist('orders'):  # если таблица orders существует
            notified_orders = db.check_dates()
            try:
                send_telegram().send(None)
                #send_telegram(notified_orders)
            except StopIteration as _ex:
                print("[INFO] Error with coroutine: ", _ex)
            content = convert_date(content)
            content = add_rub(content, exchange_rate)
            content = add_notif_date(content, notified_orders)
            content = convert_to_tuple(content)
            db.truncate_table_orders()
            sql_insert_orders = generate_insert_sql_request(content)
            db.run_sql_with_commit(sql_insert_orders)

            print(db.select_all_from_orders())
    except Exception as _ex:
        print("[INFO] Error with core: ", _ex)


# конвертация даты из "%d.%m.%Y" в "%Y-%m-%d"
def convert_date(content):
    for i in content:
        date_str = i[3]
        formatter_string = "%d.%m.%Y"
        datetime_object = datetime.strptime(date_str, formatter_string)
        i[3] = str(datetime_object.date())
    return content


# добавление колонки "рубли"
def add_rub(content, exchange_rate):
    for i in content:
        i.insert(3, int(float(i[2]) * exchange_rate))
    return content


# добавление колонки "notif_date"
def add_notif_date(content, notified_orders):
    for i in content:
        for y in notified_orders:
            if (i[1] == str(y)):
                i.append(str(date.today()))
        if (len(i) < 6):
            i.append('3333-03-03')
    return content


# конвертация в кортеж
def convert_to_tuple(content):
    content_tuple = []
    for i in content:
        content_tuple.append(tuple(i))
    content_tuple = tuple(content_tuple)
    return content_tuple


# генерация sql запроса для insert
def generate_insert_sql_request(content):
    sql_insert_orders = "insert into orders(pos, order_number, price_usd, price_rub, delivery_date, notif_date) values "
    for i in content:
        sql_insert_orders = sql_insert_orders + str(i) + ","
    sql_insert_orders = sql_insert_orders[:len(sql_insert_orders) - 1] + ";"
    return sql_insert_orders




# Алгоритм
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
# truncate orders
# формирую запрос для инсерта
# insert to orders
