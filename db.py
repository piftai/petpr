import os
import sqlite3

connection = sqlite3.connect('../../pythonProject/base.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    username TEXT DEFAULT 0,
    stage TEXT,
    balance TEXT DEFAULT 0,
    count_account BIGINT DEFAULT 0,
    count_video BIGINT DEFAULT 0,
    id_video BIGINT DEFAULT 0,
    link_new_video TEXT DEFAULT 0,
    id_account_work BIGINT DEFAULT 0
    )""")


cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    balance TEXT,
    status TEXT
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    link TEXT,
    type TEXT
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS instagram (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    name TEXT,
    link TEXT,
    email TEXT,
    password TEXT,
    username TEXT,
    status TEXT,
    count_video BIGINT DEFAULT 0
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS tiktok (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    name TEXT,
    link TEXT,
    email TEXT,
    password TEXT,
    status TEXT,
    count_video BIGINT DEFAULT 0
    )""")


cursor.execute("""CREATE TABLE IF NOT EXISTS youtube (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    link TEXT,
    input_info TEXT,
    count_video BIGINT DEFAULT 1
    )""")


cursor.execute("""CREATE TABLE IF NOT EXISTS verification_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    link TEXT,
    id_video TEXT,
    input_info TEXT,
    status INTEGER DEFAULT 0
    )""")


connection.commit()
connection.close()

for i in os.listdir('info_video'):
    os.rename(f"info_video/{i}", f"info_video/{i.replace('_bron.txt', '.txt').replace('_done.txt', '.txt')}")