import logging
import os

from aiogram.types import callback_query
from aiogram.utils import executor
from config import *
from aiogram import Bot, Dispatcher
from funcs import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

bot = Bot(TOKEN)
dp = Dispatcher(bot)

admin = [703194398, 7123866288, 6023096854]


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    await log_message(message)

    chat_id = message.chat.id

    all_id_drivers = get_all_id()

    if chat_id not in all_id_drivers:
        await insert_new_user_main(chat_id)
        if 'username' in message.chat:
            ex_update(f'UPDATE users SET username = "{message.chat.username}" WHERE telegram_id = {chat_id}')
            for i in admin:
                await bot.send_message(i,
                    f"Новый пользователь с номером {len(get_all_id())}"
                    f" и ником: @{message.chat.username}")
        else:
            for i in admin:
                await bot.send_message(i, f"Новый пользователь с номером {len(get_all_id())}")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Дальше")
        await bot.send_message(chat_id,
            text=read_message('start_message_1.txt'),
            reply_markup=markup,
            parse_mode='html')
    else:
        ex_update(f'UPDATE users SET stage = "main" WHERE telegram_id = {chat_id}')
        markup = get_main_markup()
        if chat_id in admin:
            # markup.add('Скачать логи')
            markup.add('Изменить баланс')
        await bot.send_message(chat_id, 'Главное меню', reply_markup=markup)


async def send_main_go(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Вступить в беседу', url='https://t.me/communityofmm'))
    update_stage(chat_id, "second_message")
    await bot.send_message(chat_id, text=read_message('start_message_2.txt'), reply_markup=markup, parse_mode='html')


async def send_second_message_go(chat_id):
    markup = get_main_markup()
    update_stage(chat_id, "main")
    await bot.send_message(chat_id,
        text=f"https://youtu.be/kBT816Jc5K0?si=YDrT1IayHjwX_X4Z\n"
            f"\nhttps://youtu.be/dc8Ll9eD1kM?si=ZsGhDFGtpQDGDDcz\n"
            f"\n{read_message('start_message_3.txt')}", reply_markup=markup, parse_mode='html',
            disable_web_page_preview=True)


async def send_personal_info(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Вывод средств")
    markup.add('Главное меню')
    update_stage(chat_id, "personal_info")
    balance = get_one_param_users('balance', chat_id)
    count_account = get_one_param_users('count_account', chat_id)
    count_video = get_one_param_users('count_video', chat_id)
    info = {'balance': balance, 'count_account': count_account, 'count_video': count_video}
    await bot.send_message(chat_id=chat_id,
        text=read_message('personal_info.txt').format(**info),
        reply_markup=markup,
        parse_mode='html')


async def send_main_menu(chat_id, stage):
    id_video = get_one_param_users('id_video', chat_id)
    if (stage == 'my_account_get_link_youtube' or stage == 'my_account_type_youtube') and id_video != 0:
        ex_update(f'UPDATE users SET stage = 0, id_video = 0 WHERE telegram_id = {chat_id}')
        os.rename(f'info_video/{id_video}_bron.txt', f'info_video/{id_video}.txt')
    markup = get_main_markup()
    if chat_id in admin:
        # markup.add('Скачать логи')
        markup.add('Изменить баланс')
    update_stage(chat_id, "main")
    await bot.send_message(chat_id=chat_id,
        text='Главное меню',
        reply_markup=markup,
        parse_mode='html')


async def send_my_account(chat_id):
    count_account = get_one_param_users('count_account', chat_id)
    update_stage(chat_id, "my_account_type_video")
    if count_account == 0:
        await bot.send_message(chat_id, text=read_message('instruction_my_account.txt'))
    markup = get_type_video_markup()

    await bot.send_message(chat_id,
        text=read_message('text_my_account.txt'),
        reply_markup=markup)


async def send_list_account_youtube(chat_id):
    list_account_youtube = get_list_account_youtube(chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить аккаунт")
    markup.add("Главное меню")

    text = ''
    count = 1
    for i in list_account_youtube:
        link, input_info = i
        text += f"{count}) Данные для входа:{input_info}\nСсылка: {link}\n\n"
        count += 1

    if text == '':
        text += 'У вас нет аккаунтов, добавьте нажав кнопку ниже'

    update_stage(chat_id, "my_account_type_youtube")

    await bot.send_message(chat_id, text, reply_markup=markup, parse_mode='html', disable_web_page_preview=True)


def get_id_video():
    list_video = [i for i in os.listdir('info_video') if ('done' not in i and 'bron' not in i)]
    if not list_video:
        return 0
    return int(list_video[0].replace('.txt', ''))


async def send_add_account_youtube(chat_id):
    update_stage(chat_id, "my_account_get_link_youtube")
    all_telegram_id = get_all_telegram_id_verif()
    if chat_id in all_telegram_id:
        update_stage(chat_id, "main")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Главное меню")
        await bot.send_message(chat_id, "Вы уже отправли заявку, ждите обработку", reply_markup=markup)
    else:
        id_video = get_id_video()
        if id_video:
            id_video_user = get_one_param_users('id_video', chat_id)
            if id_video_user == 0:
                ex_update(f"UPDATE users SET stage = 'my_account_type_youtube', id_video = {id_video} "
                    f"WHERE telegram_id = {chat_id}")
                with open(f'info_video/{id_video}.txt', 'r') as file:
                    os.rename(f"info_video/{id_video}.txt", f"info_video/{id_video}_bron.txt")
                    await bot.send_message(chat_id, f"Инструкция\n\n{file.read()}\n\nПосле того, как выложите видео -"
                                                    f" отправьте ссылку на видео")
            else:
                await bot.send_message(chat_id, "Вам уже выдали видео, отправьте ссылку на видео")

                with open(f'info_video/{id_video_user}_bron.txt', 'r') as file:
                    await bot.send_message(chat_id, f"Инструкция\n\n{file.read()}\n\nПосле того, как выложите видео -"
                                                    f" отправьте ссылку на видео")
        else:
            update_stage(chat_id, "main")
            await bot.send_message(chat_id, "Напишите ему @rustdesaba, видео закончились")


async def send_add_account_youtube_get_login_password(chat_id, text):
    if "https://youtube.com/shorts/" in text:
        ex_update(f"UPDATE users SET stage = 'my_account_get_login_password', link_new_video = '{text}'"
            f" WHERE telegram_id = {chat_id}")
        await bot.send_message(chat_id, "Ваша ссылка принята, теперь напишите логин и пароль от аккаунта ютуб")
    else:
        await bot.send_message(chat_id, "Проверьте правильность ссылки, похоже вы ввели что-то нет так")


async def send_add_account_youtube_check_verification_account(chat_id, text):
    id_video = get_one_param_users('id_video', chat_id)
    link_new_video = get_one_param_users('link_new_video', chat_id)
    with open(f'info_video/{id_video}_bron.txt', 'r') as file:
        markup = types.InlineKeyboardMarkup()
        all_tg_id_verification_account_list = all_tg_id_verification_account()
        if chat_id not in all_tg_id_verification_account_list:
            id_requst = get_id_insert_video_youtube(chat_id, id_video, link_new_video, text)
        else:
            id_requst = return_id_where_telegram_verification_account(chat_id)
        markup.add(types.InlineKeyboardButton("Подтвердрить", callback_data=f'test_video_yes_{id_requst}'))
        markup.add(types.InlineKeyboardButton("Отменить", callback_data=f'test_video_no_{id_requst}'))
        username = get_one_param_users('username', chat_id)
        text_request = (f'Новая завяка на поддтверждение <b>АККАУНТА</b> от @{username}\n\nДанные от аккаунта: \n{text}\n\n'
                        f'Ссылка: {link_new_video}'
                        f'\n\nИнформация о видео: {file.read()}')
        for i in admin:
            await bot.send_message(i, text_request, reply_markup=markup, parse_mode='html')
    update_stage(chat_id, "main")
    markup = get_main_markup()
    await bot.send_message(chat_id, "Ваша заявка отправленна на рассмотрение модератору, ожидайте", reply_markup=markup)


async def send_go_work(chat_id):
    update_stage(chat_id, "go_work_type")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Instagram')
    markup.add('Tik-Tok')
    markup.add('YouTube Shorts')
    markup.add('Главное меню')
    await bot.send_message(chat_id, '''Выберите платформу на которую будете добавлять видео''', reply_markup=markup)


async def send_account_number_work_youtube(chat_id):
    update_stage(chat_id, "go_work_type_account")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    all_account_youtube_user_info = all_account_youtube_user(chat_id)
    if all_account_youtube_user_info:
        string = ''
        for i in all_account_youtube_user_info:
            id_account, info_account = i
            markup.add(f'{id_account}')
            string += f'{id_account}) {info_account}\n'
        markup.add("Главное меню")
        await bot.send_message(chat_id, f"Выберите с какого аккаунта хотите выложить видео\n"
                                        f"Вот информация о ваших аккаунтах:\n{string}", reply_markup=markup)
    else:
        await bot.send_message(chat_id, "У вас нет верефицированных аккаунтов, вернитесь в меню и добавьте их",
            reply_markup=markup)


async def send_video_account_youtube_work(chat_id, text):
    id_account = int(text)
    ex_update(f"UPDATE users SET stage = 'get_link_work_video', "
        f"id_account_work = {id_account} WHERE telegram_id = {chat_id}")

    all_telegram_id = get_all_telegram_id_verif()
    if chat_id in all_telegram_id:
        update_stage(chat_id, "main")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Главное меню")
        await bot.send_message(chat_id, "Вы уже отправли заявку, ждите обработку", reply_markup=markup)
    else:
        id_video = get_id_video()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Главное меню")
        if id_video:
            id_video_user = get_one_param_users('id_video', chat_id)
            info_video = open(f'info_video/{id_video}.txt').read()
            if id_video_user == 0:
                ex_update(f"UPDATE users SET id_video = {id_video} "
                          f"WHERE telegram_id = {chat_id}")
                os.rename(f"info_video/{id_video}.txt", f"info_video/{id_video}_bron.txt")
                await bot.send_message(chat_id, f"Инструкция\n\n{info_video}\n\nПосле того, как выложите видео -"
                                                f" отправьте ссылку на видео", reply_markup=markup)
            else:
                await bot.send_message(chat_id, "Вам уже выдали видео, отправьте ссылку на видео")

                with open(f"info_video/{id_video_user}_bron.txt", 'r') as file:
                    await bot.send_message(chat_id, f"Инструкция\n\n{file.read()}\n\nПосле того, как выложите видео -"
                                                    f" отправьте ссылку на видео", reply_markup=markup)
        else:
            update_stage(chat_id, "main")
            await bot.send_message(chat_id, "Напишите ему @rustdesaba, видео закончились")


async def send_request_work_youtube(chat_id, text):
    if "https://youtube.com/shorts/" in text:
        ex_update(f"UPDATE users SET stage = 'main', link_new_video = '{text}' WHERE telegram_id = {chat_id}")
        id_video = get_one_param_users('id_video', chat_id)
        link_new_video = text
        markup = types.InlineKeyboardMarkup()
        id_account = get_one_param_users('id_account_work', chat_id)
        info_account = get_input_info_account_youtube(id_account)
        all_tg_id_verification_account_list = all_tg_id_verification_account()
        if chat_id not in all_tg_id_verification_account_list:
            id_requst = get_id_insert_video_youtube(chat_id, id_video, link_new_video, info_account)
        else:
            id_requst = return_id_where_telegram_verification_account(chat_id)
        markup.add(types.InlineKeyboardButton("Подтвердрить", callback_data=f'work_video_yes_{id_requst}'))
        markup.add(types.InlineKeyboardButton("Отменить", callback_data=f'work_video_no_{id_requst}'))
        info_video = open(f'info_video/{id_video}_bron.txt').read()
        username = get_one_param_users('username', chat_id)
        text_request = (f'Новая завяка на поддтверждение <b>ВИДЕО</b> от @{username}\n\nДанные от аккаунта: {info_account}\n\n'
                        f'Ссылка: {link_new_video}'
                        f'\n\nИнформация о видео: {info_video}')
        for i in admin:
            await bot.send_message(i, text_request, reply_markup=markup, parse_mode='html')
        markup = get_main_markup()
        await bot.send_message(chat_id, "Ваша заявка отправленна "
                                        "на рассмотрение модератору, ожидайте", reply_markup=markup)
    else:
        await bot.send_message(chat_id, "С ссылкой что-то не так, пожалуйста, отправьте ещё раз")


async def edit_balance(chat_id):
    update_stage(chat_id, 'edit_balance_username')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Главное меню")
    for i in get_all_id_with_username():
        markup.add(f'{i[0]}@{i[1]}')
    markup.add("Главное меню")
    await bot.send_message(chat_id, 'Нажмите на кнопку, чей баланс хотите поменять', reply_markup=markup)


async def edit_balance_get_digit(chat_id, text):
    telegram_id = int(text.split('@')[0])
    ex_update(f'UPDATE users SET stage = "get_id_balance_edit", balance = "{telegram_id}" WHERE telegram_id = {chat_id}')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Главное меню")
    await bot.send_message(chat_id, "Введите новый баланс", reply_markup=markup)


async def edit_balance_done(chat_id, text):
    new_balance = int(text)
    telegram_id = int(get_one_param_users('balance', chat_id))
    ex_update(f'UPDATE users SET stage = "balance_done", balance = "0" WHERE telegram_id = {chat_id}')
    ex_update(f'UPDATE users SET balance = "{new_balance}" WHERE telegram_id = {telegram_id}')
    await bot.send_message(chat_id, "Вы успешно изменили баланс")


@dp.message_handler(content_types='text')
async def message_handler(message: types.Message):
    chat_id = message.chat.id
    username = get_one_param_users('username', chat_id)
    await log_message(message, username)
    stage = ex_get_stage(chat_id)
    text = message.text
    if text == 'Главное меню':
        await send_main_menu(chat_id, stage)
    elif text == 'Изменить баланс' and stage == 'main':
        await edit_balance(chat_id)
    elif stage == 'get_id_balance_edit':
        await edit_balance_done(chat_id, text)
    elif stage == 'edit_balance_username':
        await edit_balance_get_digit(chat_id, text)
    elif stage == 'start_registration' and text == 'Дальше':
        await send_main_go(chat_id)
    elif stage == 'second_message' and text == 'Дальше':
        await send_second_message_go(chat_id)
    elif stage == 'main' and text == 'Личный кабинет':
        await send_personal_info(chat_id)
    elif stage == 'main' and text == 'Мои аккаунты':
        await send_my_account(chat_id)
    # YouTube
    elif stage == 'my_account_type_video' and text == 'YouTube Shorts':
        await send_list_account_youtube(chat_id)
    elif stage == 'my_account_type_youtube' and text == 'Добавить аккаунт':
        await send_add_account_youtube(chat_id)
    elif stage == 'my_account_get_link_youtube' or stage == 'my_account_type_youtube':
        await send_add_account_youtube_get_login_password(chat_id, text)
    elif stage == 'my_account_get_login_password':
        await send_add_account_youtube_check_verification_account(chat_id, text)
    # Начать работу
    elif stage == 'main' and text == 'Начать работу':
        await send_go_work(chat_id)
    elif stage == 'go_work_type' and text == 'YouTube Shorts':
        await send_account_number_work_youtube(chat_id)
    elif stage == 'go_work_type_account':
        await send_video_account_youtube_work(chat_id, text)
    elif stage == 'get_link_work_video':
        await send_request_work_youtube(chat_id, text)
    # Вывод средств
    elif stage == 'personal_info' and text == 'Вывод средств':
        await bot.send_message(chat_id, "Напишите @rustdesaba для вывода средств")
    elif stage == 'main' and text == 'Служба поддержки':
        await bot.send_message(chat_id,
            "Напишите @rustdesaba и задайте свой вопрос\n\nБеседа: https://t.me/communityofmm")
    else:
        await bot.send_message(chat_id, 'Не знаю что ответить')


async def callback_add_account_yes(callback, message):
    id_requst = int(callback.replace('test_video_yes_', ''))
    telegram_id, link, id_video, input_info, status = get_all_verification_account(id_requst)

    os.rename(f'info_video/{id_video}_bron.txt', f'info_video/{id_video}_done.txt')
    delite_verif_account_string(id_requst)
    ex_update(f"UPDATE users SET id_video = 0, link_new_video = '0', "
              f"count_account = count_account + 1 WHERE telegram_id = {telegram_id}")
    insert_youtube_account(telegram_id, link, input_info)
    await bot.send_message(telegram_id, f"Ваш акканут с данными:\n{input_info} успешно добавлен")
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                text='✅\n' + message.message.text)
    insert_video_youtube(telegram_id, link, 'youtube')


async def callback_cancel_account_yes(callback, message):
    id_requst = int(callback.replace('test_video_no_', ''))

    telegram_id, link, id_video, input_info, status = get_all_verification_account(id_requst)

    delite_verif_account_string(id_requst)

    await bot.send_message(telegram_id, f"Ваш акканут с данными:\n{input_info} "
                                        f"отклонён, вы ввели что-то неправильно, проверьте данные "
                                        f"для входа и правильность выкладки выдео")
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                text='❌\n' + message.message.text)


async def callback_accept_video_yes(callback, message):
    id_requst = int(callback.replace('work_video_yes_', ''))
    telegram_id, link, id_video, input_info, status = get_all_verification_account(id_requst)
    delite_verif_account_string(id_requst)
    id_account_youtube = get_one_param_users('id_account_work', telegram_id)
    ex_update(f"UPDATE youtube SET count_video = count_video + 1 WHERE id = {id_account_youtube}")
    os.rename(f'info_video/{id_video}_bron.txt', f'info_video/{id_video}_done.txt')
    ex_update(f"UPDATE users SET id_video = 0, link_new_video = '0', balance = balance + 15,"
              f"count_video = count_video + 1 WHERE "
              f"telegram_id = {telegram_id}")
    await bot.send_message(telegram_id, f"Ваше видео принято от аккаунта с данными:\n{input_info}")
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                text='✅\n' + message.message.text)
    insert_video_youtube(telegram_id, link, 'youtube')


async def callback_accept_video_no(callback, message):
    id_requst = int(callback.replace('work_video_no_', ''))

    telegram_id, link, id_video, input_info, status = get_all_verification_account(id_requst)

    delite_verif_account_string(id_requst)

    await bot.send_message(telegram_id, f"Ваш акканут с данными:\n{input_info} "
                                        f"отклонён, вы ввели что-то неправильно, проверьте данные "
                                        f"для входа и правильность выкладки выдео")
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                   text='❌\n' + message.message.text)


@dp.callback_query_handler(lambda x: x != 0)
async def callback_handler(message: callback_query):
    callback = message.data
    if 'test_video_yes_' in callback:
        await callback_add_account_yes(callback, message)
    elif 'test_video_no_' in callback:
        await callback_cancel_account_yes(callback, message)
    elif 'work_video_yes_' in callback:
        await callback_accept_video_yes(callback, message)
    elif 'work_video_no_' in callback:
        await callback_accept_video_no(callback, message)


executor.start_polling(dp, skip_updates=True)
