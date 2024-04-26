import sqlite3

connection = sqlite3.connect('base.db')
cursor = connection.cursor()

cursor.execute("DROP TABLE verification_account")

cursor.execute("""CREATE TABLE IF NOT EXISTS verification_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    link TEXT,
    id_video TEXT,
    input_info TEXT,
    status INTEGER DEFAULT 0
    )""")

cursor.execute(f'''UPDATE users SET stage = "main", id_video = 0, link_new_video = "0", id_account_work = 0''')

connection.commit()
connection.close()

