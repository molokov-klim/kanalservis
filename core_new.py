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
                notified_orders = check_dates(cursor)
                # print("notified_orders")                            ####
                # print(notified_orders)                              ####
                content = convert_date(content)
                content = add_rub(content, exchange_rate)
                content = add_notif_date(content, notified_orders)
                content = convert_to_tuple(content)
                cursor.execute('truncate orders')
                connection.commit()
                sql_insert_orders = generate_insert_sql_request(content)
                cursor.execute(sql_insert_orders)
                connection.commit()

                cursor.execute('select * from orders')
                print(cursor.fetchall())


    except Exception as _ex:
        print("[INFO] Error while working with PostrgeSQL ", _ex)

    finally:
        if connection:
            connection.close()


# проверка дат уведомлений в БД. возвращает список заказов с сегодняшней датой уведомления
def check_dates(cursor):
    cursor.execute("select * from orders")
    orders = cursor.fetchall()
    notified_orders = ()
    for i in orders:
        if (i[5] < date.today()):  # если срок поставки вышел
            if (i[6] == date.today()):  # если уведомление сегодня
                notified_orders = notified_orders + (i[2],)
            if (i[6] != date.today()):  # если уведомление не сегодня
                send_telegram(i)
                notified_orders = notified_orders + (i[2],)
    print("notified_orders")
    print(notified_orders)
    return notified_orders


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


#конвертация в кортеж
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
