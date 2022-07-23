from datetime import date
import psycopg2
from config import HOST, PORT, USER, PASSWORD, DB_NAME


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

    # проверка существует ли таблица
    def is_exist(self, table):
        with self.connection:
            self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table,))
            result = self.cursor.fetchone()[0]
            return result

    # ----------------------------------------ORDERS---------------------------------------------------------------

    # проверка дат уведомлений в БД. возвращает список просроченных заказов
    def check_dates(self):
        with self.connection:
            self.cursor.execute("select * from orders")
            orders = self.cursor.fetchall()
            notified_orders = ()
            for i in orders:
                if i[4] < date.today():  # если срок поставки вышел
                    if i[5] == date.today():  # если уведомление сегодня
                        notified_orders = notified_orders + (i[1],)
                    if i[5] != date.today():  # если уведомление не сегодня
                        notified_orders = notified_orders + (i[1],)
            return notified_orders

    # очистка таблицы orders
    def truncate_table_orders(self):
        with self.connection:
            self.cursor.execute('truncate orders')
            self.connection.commit()
            return

    # выполнение sql запроса с коммитом
    def run_sql_with_commit(self, sql):
        with self.connection:
            self.cursor.execute(sql)
            self.connection.commit()
            return

    # проверка даты уведомления
    def check_notified_orders(self, notified_orders):
        sql = ""
        for i in notified_orders:
            sql = sql + "select pos, order_number, price_usd, price_rub, delivery_date, notif_date from orders where order_number = " + str(i) + " and notif_date!=CURRENT_DATE union "
        sql = sql[:len(sql) - 7]
        with self.connection:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result

    # выбор всех полей из таблицы orders
    def select_all_from_orders(self):
        with self.connection:
            self.cursor.execute('select * from orders')
            result = self.cursor.fetchall()
            return result

    # ----------------------------------------USERS---------------------------------------------------------------

    # проверка наличия пользователя в таблицу users
    def user_exists(self, user_id):
        with self.connection:
            self.cursor.execute("""select * from users where user_id = %s""", (user_id,))
            result = self.cursor.fetchmany(1)
            return bool(len(result))

    # добавление пользователя в таблицу users
    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute("""insert into users (user_id) values (%s)""", (user_id,))
            self.connection.commit()
            return

    # установка флага active для пользователя в таблице users
    def set_active(self, user_id, active):
        with self.connection:
            self.cursor.execute("""update users set active = %s where user_id = %s""", (active, user_id,))
            self.connection.commit()
            return

    # выбрать пользователей из таблицы users
    def get_users(self):
        with self.connection:
            self.cursor.execute("select user_id, active from users")
            result = self.cursor.fetchall()
            return result


