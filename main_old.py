import aiogram
import asyncio
from config import TOKEN
from aiogram.types import message, callback_query, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher
from db import execute_mysql as ex
import re

bot = Bot(TOKEN)
dp = Dispatcher(bot)

admin = 703194398 

# 728420168

# TODO сделать админов по циклу


def create_start_markup() -> aiogram.types.ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Баланс")
    markup.add("Заказы")
    # markup.add("Подключить канал") 
    # markup.add("Мои каналы") # TODO сделать подключение канал и выбор при отклике + сделать у видоса (заявки) список с уже откликнушився
    markup.add("Реферальная система")
    markup.add("Техническая поддержка")
    return markup

def create_order_markup(list_order) -> aiogram.types.ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in list_order:
        markup.add(f'ID: {i[0]} | Выполненно: {i[1]}/{i[2]}')
    return markup



async def balance(message: message):
    chat_id = message.chat.id
    stage = ex(f'SELECT stage FROM users WHERE telegram_id = {chat_id}')[0][0]
    if message.text == 'Баланс':
        ex(f'UPDATE users SET stage = "balance" WHERE telegram_id = {chat_id}')

        balance = ex(f'SELECT balance FROM users WHERE telegram_id = {chat_id}')[0][0]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Вывести деньги")
        markup.add("Вернуться в меню")
        await bot.send_message(chat_id, f'Ваш баланс: {balance}', reply_markup=markup)
    elif message.text == 'Вывести деньги':
        ex(f'UPDATE users SET stage = "withdraw_money" WHERE telegram_id = {chat_id}')
        all_telegram_id_from_application = {i[0] for i in ex(f'SELECT telegram_Id FROM application')}
        if chat_id in all_telegram_id_from_application: # Заявка уже есть
            await bot.send_message(chat_id, 'Вы уже оставили заявку, подожди когда её одобрят или напиши в тех поддержку')
        else: # Завяки нет, делаем новую
            balance = ex(f'SELECT balance FROM users WHERE telegram_id = {chat_id}')[0][0]
            await check_for_output_conditions(chat_id, balance)

    elif stage == 'count_withdraw':
        ex(f'UPDATE users SET stage = "forming_application" WHERE telegram_id = {chat_id}')
        try:
            balance = ex(f'SELECT balance FROM users WHERE telegram_id = {chat_id}')[0][0]
            count_withdraw = int(message.text.split('/')[0])
            if 200 <= count_withdraw <= balance:
                phone = message.text.split('/')[1]
                ex(f'INSERT INTO application(telegram_id, count_withdraw, phone) VALUE({chat_id}, {count_withdraw}, "{phone}")')
                id_application = ex(f'SELECT id FROM application WHERE telegram_id = {chat_id}')[0][0]

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Выполненно', callback_data=str(id_application) + '_money'))

                new_application = f'Новая заявка на вывод\nНомер: {phone}\nДеньги: {count_withdraw}'

                await bot.send_message(admin, new_application, reply_markup=markup)
                await bot.send_message(chat_id, 'Заявка отправлена')
            else:
                ex(f'UPDATE users SET stage = "count_withdraw" WHERE telegram_id = {chat_id}')
                await bot.send_message(chat_id, f'Введите сумму >= 200 и <= ВАШ БАЛАНС\nВаш баланс: {balance}')
        except Exception as e:

            await bot.send_message(chat_id, 'Похоже вы неправильно ввели сумму')



async def check_for_output_conditions(chat_id, balance):
    if balance >= 200:
        ex(f'UPDATE users SET stage = "count_withdraw" WHERE telegram_id = {chat_id}')
        await bot.send_message(chat_id, 'Введите количество денег для вывода и номер телеонфа через "/"\nПример: 350/88005553535')
    else:
        await bot.send_message(chat_id, 'Вывод доступен от 200 рублей')


async def help(message: message):
    chat_id = message.chat.id
    ex(f'UPDATE users SET stage = "help" WHERE telegram_id = {chat_id}')
    await bot.send_message(chat_id, "Напиши в тех поддержку\n@SaNcHeZ2222")



async def main_menu(message: message):
    chat_id = message.chat.id
    ex(f'UPDATE users SET stage = "main_menu" WHERE telegram_id = {chat_id}')
    markup = create_start_markup()
    await bot.send_message(chat_id, 'Ты в главном меню', reply_markup=markup)


async def order(message: message):
    chat_id = message.chat.id
    stage = ex(f"SELECT stage FROM users WHERE telegram_id = {chat_id}")[0][0]


    if message.text == 'Заказы' or message.text == 'Обновить':
        list_order = ex('SELECT id, count_done, count_need FROM booking')
        markup = create_order_markup(list_order)
        markup.add("Обновить")
        markup.add("Вернуться в меню")
        ex(f'UPDATE users SET stage = "booking" WHERE telegram_id = {chat_id}')
        await bot.send_message(chat_id, 'Вот список заказов', reply_markup=markup)
    elif 'ID' in message.text:
            id = get_valid_id_order(message)
            if id != 0:
                ex(f'UPDATE users SET stage = "{id}_order" WHERE telegram_id = {chat_id}')
                order_info = ex(f"SELECT instruction, price FROM booking WHERE id = {id}")[0]

                await bot.send_message(chat_id, f"Вот инструкция: {order_info[0]}\n\nPrice: {order_info[1]}\n\nКак выполните - отправьте ссылку на видео и ваш комментарий под этим сообщением (СТРОГО ПОД НИМ)")
            else: 
                  await bot.send_message(chat_id, 'Неверный ID заказа')
    elif '_order' in stage and 'id' not in stage:

        id_video = int(stage.split("_")[0])
        ex(f'INSERT INTO checkOrder(telegram_id, info, checks) VALUE({chat_id}, "{message.text}", {id_video})')
        id_order = ex(f'SELECT id FROM checkOrder WHERE telegram_id = {chat_id} ORDER BY id DESC LIMIT 1 ')[0][0]
        ex(f'UPDATE users SET stage = "{stage}_check_oder" WHERE telegram_id = {chat_id}')

        all_info_video = ex(f"SELECT instruction, price, count_need, count_done FROM booking WHERE id = {id_video}")[0]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Всё правильно!', callback_data=str(id_order) + '_check'))
        markup.add(InlineKeyboardButton('Отклонить', callback_data=str(id_order) + '_decline'))
        await bot.send_message(admin, f"Новая заявка на видео\nИнфа: {all_info_video[0]}\nЦена: {all_info_video[1]}\nЦель: {all_info_video[3]}/{all_info_video[2]}\nЗаказ: {message.text}", reply_markup=markup)
        await bot.send_message(chat_id, 'Ваша заявка отправлена на рассмотрение')


def get_valid_id_order(message: message):
    chat_id = message.chat.id
    ex(f'UPDATE users SET stage = "id_order" WHERE telegram_id = {chat_id}')
    try:
        id = int(message.text.split('ID: ')[1][0])
        if id in {i[0] for i in ex("SELECT id FROM booking")}:
            return id
        else: 
            return 0

    except Exception as e:
      
        return 0


async def registration(message: message):
    chat_id = message.chat.id
    stage = ex(f'SELECT stage FROM users WHERE telegram_id = {chat_id}')[0][0]
    if message.text == 'Регистрация' and stage == 'reg':
        ex(f"UPDATE users SET stage = 'test_video' WHERE telegram_id = {chat_id}")
        await bot.send_message(chat_id, 'Инструкция с тестовым видосом')
    elif stage == 'test_video':
        id_video = -100
        ex(f'INSERT INTO checkOrder(telegram_id, info, checks) VALUE({chat_id}, "{message.text}", {id_video})')
        id_order = ex(f'SELECT id FROM checkOrder WHERE telegram_id = {chat_id} ORDER BY id DESC LIMIT 1 ')[0][0]
        ex(f'UPDATE users SET stage = "{stage}_check_test_order" WHERE telegram_id = {chat_id}')
        all_info_video = 'Инструкция по тестовому видосу'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Всё правильно!', callback_data=str(id_order) + '_test_yes'))
        markup.add(InlineKeyboardButton('Отклонить', callback_data=str(id_order) + '_test_no'))
        await bot.send_message(admin, f"Новая заявка на ТЕСТ\nИнфа: {all_info_video}\nЗаказ: {message.text}", reply_markup=markup)
        await bot.send_message(chat_id, 'Ваша заявка отправлена на рассмотрение')
    else:
        await bot.send_message(chat_id, 'Не знаю что ответить!')


async def referal(message: message):
    chat_id = message.chat.id
    count_referal = len(ex(f'SELECT id FROM users WHERE referal_id = {chat_id}'))
    referal_link = f'https://t.me/youtube_piar_school_bot?start={chat_id}'
    await bot.send_message(chat_id, f'Вот ваша реферальная ссылка: {referal_link}\nКоличество зарегистровавшихся по вашей ссылке: {count_referal}\nЗа каждого зарегистрировавшегося пользователя вы будете получать на баланс 2 рубля')


@dp.message_handler(regexp='^/start\s\d+')
async def referral_handler(message: message):
    referral_chat_id = re.search(r'\d+', message.text).group(0)
    chat_id = message.chat.id
    all_telegram_id = {i[0] for i in ex("SELECT telegram_id FROM users")}
    if chat_id in all_telegram_id: # Есть в б/д 
        reg = ex(f'SELECT reg FROM users WHERE telegram_id = {chat_id}')[0][0]
        if reg == 1:
            ex(f'UPDATE users SET stage = "main_menu" WHERE telegram_id = {chat_id}')
            markup = create_start_markup()
            await bot.send_message(chat_id, 'Ты в главном меню', reply_markup=markup)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Регистрация')
            await bot.send_message(chat_id, 'Чтобы зарегистрироваться - нажми на кнопку ниже', reply_markup=markup)
    else: # Нет в бд
        ex(f"INSERT INTO users(telegram_id, stage, referal_id) VALUE ({chat_id}, 'reg', {referral_chat_id})")
        id = ex(f"SELECT id FROM users WHERE telegram_id = {chat_id}")[0][0]
        await bot.send_message(admin, f'Новый пользователь с номером {id}')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Регистрация')
        await bot.send_message(chat_id, 'Чтобы зарегистрироваться - нажми на кнопку ниже', reply_markup=markup)
#TODO 1 человек - 1 заказ (Пока не делать)


@dp.message_handler(commands='start')
async def start_message(message: message):
    chat_id = message.chat.id
    all_telegram_id = {i[0] for i in ex("SELECT telegram_id FROM users")}
    if chat_id in all_telegram_id: # Есть в б/д 
        reg = ex(f'SELECT reg FROM users WHERE telegram_id = {chat_id}')[0][0]
        if reg == 1:
            ex(f'UPDATE users SET stage = "main_menu" WHERE telegram_id = {chat_id}')
            markup = create_start_markup()
            await bot.send_message(chat_id, 'Ты в главном меню', reply_markup=markup)
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Регистрация')
            await bot.send_message(chat_id, 'Чтобы зарегистрироваться - нажми на кнопку ниже', reply_markup=markup)
    else: # Нет в бд
        ex(f"INSERT INTO users(telegram_id, stage) VALUE ({chat_id}, 'reg')")
        id = ex(f"SELECT id FROM users WHERE telegram_id = {chat_id}")[0][0]
        await bot.send_message(admin, f'Новый пользователь с номером {id}')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Регистрация')
        await bot.send_message(chat_id, 'Чтобы зарегистрироваться - нажми на кнопку ниже', reply_markup=markup)


@dp.message_handler(content_types='text')
async def text_handler(message: message):
    chat_id = message.chat.id
    stage = ex(f'SELECT stage FROM users WHERE telegram_id = {chat_id}')[0][0]
    reg = ex(f'SELECT reg FROM users WHERE telegram_id = {chat_id}')[0][0]
    if reg == 1: # Зареган
        
        if message.text == 'Баланс' or message.text == 'Вывести деньги' or stage == 'count_withdraw':
            await balance(message)
        elif message.text == 'Техническая поддержка':
            await help(message)
        elif message.text == 'Вернуться в меню':
            await main_menu(message)
        elif message.text == 'Заказы' or message.text == 'Обновить' or 'ID' in message.text or '_order' in stage:
            await order(message)
        elif message.text == 'Реферальная система':
            await referal(message)
        # TODO делать рефералку 
        # TODO сделать добавление канала + б/д ссылка на канал + telegram_id
        else:
            await bot.send_message(chat_id, 'Не знаю что ответить!')
    else: # Не зареган
        await registration(message)
        

@dp.callback_query_handler(lambda x: x != 0)
async def callback_handler(callback: callback_query):
    if 'money' in callback.data:
        id = int(callback.data.split('_')[0])
        chat_id_money = ex(f'SELECT telegram_id FROM application WHERE id = {id}')[0][0]
        balance = ex(f'SELECT balance FROM users WHERE telegram_id = {chat_id_money}')[0][0]
        count_withdraw = ex(f'SELECT count_withdraw FROM application WHERE id = {id}')[0][0]
        new_balance = balance - count_withdraw
        ex(f'DELETE FROM application WHERE id = {id}')
        ex(f'UPDATE users SET balance = {new_balance} WHERE telegram_id = {chat_id_money}')
        await bot.send_message(chat_id_money, 'Ваша заявка одобрена, средства отправлены')
        await bot.send_message(admin, 'Вы приняли заявку на БАБКИ')

    elif 'check' in callback.data:
        id_order = int(callback.data.split('_')[0])

        chat_id_check = ex(f'SELECT telegram_id FROM checkOrder WHERE id = {id_order}')[0][0]
        id_video = ex(f'SELECT checks FROM checkOrder WHERE id = {id_order}')[0][0]
        ex(f'UPDATE booking SET count_done = count_done + 1 WHERE id = {id_video}')
        price = ex(f'SELECT price FROM booking WHERE id = {id_video}')[0][0]
        ex(f'UPDATE users SET balance = balance + {price} WHERE telegram_id = {chat_id_check}')
        await bot.send_message(chat_id_check, 'Ваша заявка принята, деньги зачислены!')
        await bot.send_message(admin, 'Вы приняли заявку')


        ex(f'DELETE FROM checkOrder WHERE id = {id_order} LIMIT 1')
        count_done, count_need = ex(f'SELECT count_done, count_need FROM booking WHERE id = {id_video}')[0]

        if count_need == count_done:
            ex(f'DELETE FROM booking WHERE id = {id_video} LIMIT 1')
    elif 'decline' in callback.data:
        id_order = int(callback.data.split('_')[0])
        chat_id_decline = ex(f'SELECT telegram_id FROM checkOrder WHERE id = {id_order}')[0][0]
        ex(f'DELETE FROM checkOrder WHERE id = {id_order} LIMIT 1')
        await bot.send_message(chat_id_decline, "Ваша заявка отклонена, вы сделали что-то неправильно или выполненна норма для этого заказа")
        await bot.send_message(admin, 'Вы отклонили заявку')

    elif 'test_yes' in callback.data:
        id_test_order = int(callback.data.split('_')[0])
        chat_id_test_check = ex(f'SELECT telegram_id FROM checkOrder WHERE id = {id_test_order}')[0][0]
    
        ex(f'UPDATE users SET reg = 1, stage = "main_menu" WHERE telegram_id = {chat_id_test_check}')
        ex(f'DELETE FROM checkOrder WHERE id = {id_test_order} LIMIT 1')
        markup = create_start_markup()
        await bot.send_message(chat_id_test_check, 'Ваша заявка принята, вам доступен полный функционал!', reply_markup=markup)
        await bot.send_message(admin, 'Вы принял ТЕСТОВУЮ заявку')
        #TODO кинуть бабки рефу
    elif 'test_no' in callback.data:
        id_test_order = int(callback.data.split('_')[0])
        chat_id_test_decline = ex(f'SELECT telegram_id FROM checkOrder WHERE id = {id_test_order}')[0][0]
        ex(f'DELETE FROM checkOrder WHERE id = {id_test_order} LIMIT 1')
        ex(f'UPDATE users SET stage = "reg" WHERE telegram_id = {chat_id_test_decline}')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Регистрация')
        await bot.send_message(chat_id_test_decline, "Ваша заявка отклонена, вы сделали что-то неправильно! Нажмите на кнопку ещё раз", reply_markup=markup)
        await bot.send_message(admin, 'Вы отклонили ТЕСТОВУЮ заявку')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
