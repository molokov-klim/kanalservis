import psycopg2
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, HOST, PORT, USER, PASSWORD, DB_NAME
import requests


def db_sync_google_sheets():  # синхронизация БД и Google Sheets
    content = get_content_from_google_sheets()
    exchange_rate = get_exchange_rate()
    content = add_ruble(content, exchange_rate)
    insert_to_db(content)

def get_service():  # создает ресурс для работы с Google Sheets API
    creds_json = os.path.dirname(
        __file__) + "/creds/kanalservis_key.json"  # https://developers.google.com/workspace/guides/create-credentials
    scopes = ['https://www.googleapis.com/auth/spreadsheets']  # уровень доступа
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def get_content_from_google_sheets():  # получение контента из Google Sheets
    service = get_service()
    sheet = service.spreadsheets()
    content = sheet.values().batchGet(spreadsheetId=SHEET_ID, ranges=["Лист1"]).execute()
    return content


def get_exchange_rate(): #парсинг курса валют с ЦБ РФ
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return exchange_rate['Valute']['USD']['Value']


def add_ruble(content, exchange_rate): #добавление колонки "рубли" и преобразование в кортеж
    content = content['valueRanges'][0]['values']
    content_tuple = []
    for i in content:
        if (i[0] != '№'):
            i.insert(3, int(float(i[2])*exchange_rate))
            i = rotate_date(i)
            content_tuple.append(tuple(i))
    content_tuple = tuple(content_tuple)
    return content_tuple

def rotate_date(element):
    print(element)
    rotated_date = element[4][6]+element[4][7]+element[4][8]+element[4][9]+element[4][5]+element[4][3]+element[4][4]+element[4][2]+element[4][0]+element[4][1]
    element[4] = rotated_date
    print(element)

    return element


def insert_to_db(content):
    try:
        # открываем соединение с базой
        connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        with connection.cursor() as cursor:
            # запрос на timestamp начала диапазона
            cursor.execute(
                """ select * from orders """
                # """SELECT shiftdate, shift, shiftstart_epoch FROM shifts WHERE shiftstart_epoch >= %s AND shiftstart_epoch <= %s""",
                # (USER_RANGE[4], USER_RANGE[5])
            )
            #RANGE_LIST = cursor.fetchall()
            #print(cursor.fetchall())
            #return RANGE_LIST

    except Exception as _ex:
        print("[INFO] Error while working with PostrgeSQL ", _ex)

    finally:
        if connection:
            connection.close()


