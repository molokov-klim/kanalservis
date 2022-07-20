from core import db_sync_google_sheets, get_service
from time import sleep


def init():
    service = get_service()

    while True:
        sleep(0)
        db_sync_google_sheets(service)


if __name__ == '__main__':
    init()








