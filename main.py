from core import db_sync_google_sheets
from time import sleep


def init():
    while True:
        sleep(0)
        db_sync_google_sheets()


if __name__ == '__main__':
    init()








