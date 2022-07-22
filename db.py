from datetime import datetime, date
import psycopg2
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, HOST, PORT, USER, PASSWORD, DB_NAME
from telegram import send_telegram
import requests

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        self.cursor = self.connection.cursor()

    def test(self, message):
        with self.connection:
            print(type(message))
            self.cursor.execute("""select pos from orders where pos > %s""", (message,))
            result = self.cursor.fetchall()
            print(result)
            return result

    #существует ли таблица
    def is_exist(self, table):
        with self.connection:
            self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table,))
            result = self.cursor.fetchone()[0]
            return result

    # проверка дат уведомлений в БД. возвращает список заказов с сегодняшней датой уведомления
    def check_dates(self):
        with self.connection:
            self.cursor.execute("select * from orders")
            orders = self.cursor.fetchall()
            notified_orders = ()
            print("orders")
            print(orders)
            for i in orders:
                if i[4] < date.today():  # если срок поставки вышел
                    if i[5] == date.today():  # если уведомление сегодня
                        notified_orders = notified_orders + (i[1],)
                    if i[5] != date.today():  # если уведомление не сегодня
                        send_telegram(i)
                        notified_orders = notified_orders + (i[1],)
            print("notified_orders")
            print(notified_orders)
            return notified_orders

    # очистка таблицы orders
    def truncate_table_orders(self):
        with self.connection:
            self.cursor.execute('truncate orders')
            self.connection.commit()

    # выполнение sql запроса с коммитом
    def run_sql_with_commit(self, sql):
        with self.connection:
            self.cursor.execute(sql)
            self.connection.commit()

    # выбор всех полей из таблицы orders
    def select_all_from_orders(self):
        with self.connection:
            self.cursor.execute('select * from orders')
            result = self.cursor.fetchall()
            return result


