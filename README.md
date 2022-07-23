Условия развертки:
Установить значения полей в config.py
Терминал (venv): pip install -r req.txt
Postgresql: CREATE TABLE orders (pos smallint, order_number integer, price_usd integer, price_rub integer, delivery_date date, notif_date date);
Postgresql: CREATE TABLE users (id serial primary key, user_id integer unique not null, active integer default (1));
В корне проекта создать папку "creds", в нее поместить файл kanalservis_key.json (https://developers.google.com/workspace/guides/create-credentials)

Ссылка на Google Sheets:
https://docs.google.com/spreadsheets/d/1iVCAfezZmbweo5AMx1L_clopNoiR2TkOsyroXUgiMAE/edit#gid=0

Статус:
пп 4 требований - в разработке
