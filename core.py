from datetime import datetime, date
import psycopg2
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, HOST, PORT, USER, PASSWORD, DB_NAME
from telegram import send_telegram
import requests


# синхронизация БД и Google Sheets
def db_sync_google_sheets(service):
    content = get_content_from_google_sheets(service)
    exchange_rate = get_exchange_rate()
    content = add_ruble(content, exchange_rate)
    insert_to_db(content)


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
    return content


# парсинг курса валют с ЦБ РФ
def get_exchange_rate():
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return exchange_rate['Valute']['USD']['Value']


# добавление колонки "рубли" и преобразование в кортеж
def add_ruble(content, exchange_rate):
    content = content['valueRanges'][0]['values']
    content_tuple = []
    for i in content:
        if (i[0] != '№'):
            i.insert(3, int(float(i[2]) * exchange_rate))
            if (len(i)!=6):
                 i.append("3333-01-01")
            i = convert_date(i)
            content_tuple.append(tuple(i))
    content_tuple = tuple(content_tuple)
    return content_tuple


# конвертация даты
def convert_date(element):
    date_str = element[4]
    formatter_string = "%d.%m.%Y"
    datetime_object = datetime.strptime(date_str, formatter_string)
    if(datetime_object.date()<date.today()):
         current_date = str(date.today())
         element[5] = current_date
    element[4] = str(datetime_object.date())
    return element


# обновление таблицы в базе
def insert_to_db(content):
    sql_drop_orders = "DROP TABLE orders;"
    sql_create_orders = "CREATE TABLE orders (id smallserial PRIMARY KEY, pos smallint, order_number integer, price_usd integer, price_rub integer, delivery_date date, notif_date date);"
    sql_insert_orders = "insert into orders(pos, order_number, price_usd, price_rub, delivery_date, notif_date) values "
    for i in content:
        sql_insert_orders = sql_insert_orders + str(i) + ","
    sql_insert_orders = sql_insert_orders[:len(sql_insert_orders) - 1] + ";"

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
                check_date(cursor)
                cursor.execute(sql_drop_orders)
                cursor.execute(sql_create_orders)
                connection.commit()
            else:
                cursor.execute(sql_create_orders)
                connection.commit()
            cursor.execute(sql_insert_orders)
            connection.commit()
            cursor.execute("select * from orders")
            print("cursor")
            print(cursor.fetchall())

    except Exception as _ex:
        print("[INFO] Error while working with PostrgeSQL ", _ex)

    finally:
        if connection:
            connection.close()

def check_date(cursor):
    cursor.execute("select * from orders")
    print("check_date")
    print(cursor.fetchall())