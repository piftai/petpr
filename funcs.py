import datetime
import sqlite3
from aiogram import types


def read_message(name: str):
    with open(f'files/{name}', 'r') as file:
        in_file = file.read()
        return in_file


def ex_update(request: str):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(request)

    connection.commit()
    connection.close()


def get_all_id() -> set:
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    all_id_drivers = {i[0] for i in cursor.execute('SELECT telegram_id FROM users')}

    connection.commit()
    connection.close()

    return all_id_drivers


def get_all_telegram_id_verif() -> set:
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    all_id_drivers = {i[0] for i in cursor.execute('SELECT telegram_id FROM verification_account')}

    connection.commit()
    connection.close()

    return all_id_drivers





def get_all_id_with_username() -> set:
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    all_id_drivers = {i for i in cursor.execute('SELECT telegram_id, username FROM users')}

    connection.commit()
    connection.close()

    return all_id_drivers

async def insert_new_user_main(chat_id) -> None:
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f"INSERT INTO users(telegram_id, stage) VALUES ({chat_id}, 'start_registration')")

    connection.commit()
    connection.close()


def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Личный кабинет')
    markup.add('Начать работу')
    markup.add('Мои аккаунты')
    markup.add('Служба поддержки')

    return markup


def ex_get_stage(chat_id: int) -> str:
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT stage FROM users WHERE telegram_id = {chat_id}')
    stage = cursor.fetchall()[0][0]

    connection.commit()
    connection.close()

    return stage


def update_stage(chat_id, stage):
    ex_update(f'UPDATE users SET stage = "{stage}" WHERE telegram_id = {chat_id}')


def get_one_param_users(param, chat_id):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT {param} FROM users WHERE telegram_id = {chat_id}')
    param = cursor.fetchall()[0][0]

    connection.commit()
    connection.close()

    return param


async def log_message(message: types.Message, username=0):
    from_user = message.from_user
    text = message.text
    if username == '0':
        log_entry = f'Сообщение {datetime.datetime.now().strftime("%d-%m-%y %H:%M")} от {from_user.full_name} c id {message.chat.id}: {text}\n'
    else:
        log_entry = f'Сообщение {datetime.datetime.now().strftime("%d-%m-%y %H:%M")} от {from_user.full_name} с ником {username} c id {message.chat.id}: {text}\n'
    with open('log_file.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)


def get_type_video_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Instagram')
    markup.add('Tik-Tok')
    markup.add('YouTube Shorts')
    return markup


def get_list_account_youtube(chat_id):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    email_password_youtube = {i for i in cursor.execute(
        f'SELECT link, input_info FROM youtube WHERE telegram_id = {chat_id}')}

    connection.commit()
    connection.close()

    return email_password_youtube


def get_id_insert_video_youtube(chat_id, id_video, link, text):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(
        f"INSERT INTO verification_account(telegram_id, id_video, link, input_info) "
        f"VALUES ({chat_id}, '{id_video}', '{link}', '{text}')")
    connection.commit()
    id_requst = cursor.lastrowid
    connection.close()
    return id_requst


def get_all_verification_account(id_stirng):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT telegram_id, link, id_video, input_info, status'
                   f' FROM verification_account WHERE id = {id_stirng}')
    all_info = cursor.fetchall()

    connection.commit()
    connection.close()

    return all_info[0]


def insert_youtube_account(telegram_id, link, input_info):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(
        f"INSERT INTO youtube(telegram_id, link, input_info) VALUES ({telegram_id}, '{link}', '{input_info}')")

    connection.commit()
    connection.close()


def all_account_youtube_user(chat_id):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    all_id_youtube_chanel = {i for i in cursor.execute(f'SELECT id, input_info FROM '
                                                       f'youtube WHERE telegram_id = {chat_id}')}

    connection.commit()
    connection.close()

    return all_id_youtube_chanel


def get_input_info_account_youtube(id_account):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT input_info FROM youtube WHERE id = {id_account}')
    id_account = cursor.fetchall()[0][0]

    connection.commit()
    connection.close()

    return id_account


def get_telegram_id_verif_account(id_video):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT telegram_id FROM verification_account WHERE (id_video = {id_video} and status = 0)')
    id_account = cursor.fetchall()[0][0]

    connection.commit()
    connection.close()

    return id_account


def delite_verif_account_string(id_requst):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()
    cursor.execute(f"DELETE from verification_account where id = {id_requst}")

    connection.commit()
    connection.close()


def insert_video_youtube(telegram_id, link, type_video):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(
        f"INSERT INTO video(telegram_id, link, type) "
        f"VALUES ({telegram_id}, '{link}', '{type_video}')")

    connection.commit()
    connection.close()


def all_tg_id_verification_account():
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    all_tg_id_verification_account = {i[0] for i in cursor.execute(f'SELECT telegram_id FROM verification_account')}

    connection.commit()
    connection.close()

    return all_tg_id_verification_account


def return_id_where_telegram_verification_account(chat_id):
    connection = sqlite3.connect('base.db', check_same_thread=True)
    cursor = connection.cursor()

    cursor.execute(f'SELECT id FROM verification_account WHERE telegram_id = {chat_id}')
    id_req = cursor.fetchall()[0][0]

    connection.commit()
    connection.close()

    return id_req
