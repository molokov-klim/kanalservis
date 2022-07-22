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

    def test(self, message):
        with self.connection:
            print(type(message))
            self.cursor.execute("""select pos from orders where pos > %s""", (message,))
            result = self.cursor.fetchall()
            print(result)
            return result

    def isExist(self, table):
        with self.connection:
            result = self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table,)).cursor.fetchone()[0]
            return result








