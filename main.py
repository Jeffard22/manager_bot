import telebot
from telebot import types
import time
from config import token_api
from intro_text import intro_text
import markups as mark
import sqlite3

my_id = "742793551"  # Ваш айди куда будет приходить сообщения с информацией о юзере и его заявке


def get_info_user(bot, message, contact_info=None):  # функция для отправки информации о юзере в личку
    if contact_info:
        bot.send_message(my_id, f"{message.text} {contact_info} "
                         + f'{message.chat.id}' + ' '
                         + f'{message.from_user.first_name}' + ' '
                         + f'{message.from_user.last_name}')
    else:
        bot.send_message(my_id, f"{message.text} "
                         + f'{message.chat.id}' + ' '
                         + f'{message.from_user.first_name}' + ' '
                         + f'{message.from_user.last_name}')


def run_bot():
    bot = telebot.TeleBot(token_api)

    @bot.message_handler(commands=['start'])  # приветственная функция
    def send_welcome(message):

        conn = sqlite3.connect('users_manager_bot.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
           userid INT PRIMARY KEY,
           fname TEXT,
           lname TEXT);
        """)
        conn.commit()

        user_info = (f'{message.chat.id}',
                     f'{message.from_user.first_name}',
                     f'{message.from_user.last_name}')

        cur.execute("INSERT OR IGNORE INTO users VALUES(?, ?, ?);", user_info)  # если есть такая запись не записывать
        conn.commit()

        img = open('title.jpg', 'rb')
        bot.send_photo(message.chat.id, img)
        welcome_user = f'Здравствуйте {message.from_user.first_name} {message.from_user.last_name}' + intro_text

        bot.send_message(message.chat.id, welcome_user,
                         reply_markup=mark.main_menu)

    @bot.message_handler(content_types=['text'])
    def send_markup(message):
        if message.text == 'Мне нужна помощь, что-то сломалось или не работает':
            bot.send_message(message.chat.id, 'Хорошо! Опишите своими словами '
                                              'что у вас случилось и в конце своего описания поставьте символ @ '
                                              '\nчто-бы я понял Вас.', reply_markup=mark.del_markup)
        elif '@' in message.text:
            bot.send_message(message.chat.id, 'Принято!',
                             reply_markup=mark.del_markup)
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
            keyboard.add(button)
            bot.send_message(message.chat.id, "Поделитесь своим номером телефона, нажав на кнопку ниже:",
                             reply_markup=keyboard)
        elif message.text == 'Назад':
            img = open('title.jpg', 'rb')
            bot.send_photo(message.chat.id, img)
            bot.send_message(message.chat.id, intro_text,
                             reply_markup=mark.main_menu)
        else:
            bot.send_message(message.chat.id, 'Я Вас не понял =(')

    @bot.message_handler(content_types=['contact'])  # обработка контактов
    def handle_contact(message):
        bot.send_message(message.chat.id, 'Спасибо, с Вами свяжутся в ближайшее время!',
                         reply_markup=mark.del_markup)
        contact_info = f"{message.text} {message.contact.phone_number}" if message.contact else None
        get_info_user(bot, message, contact_info)

    @bot.message_handler(commands=['stop'])
    def stop_bot(message):
        global running
        running = False
        bot.send_message(message.chat.id, "Бот остановлен.")

    while True:  # функция для пулинга
        print('=^.^=', 'ver 1.0')  # информация о статусе бота в коммандной строке

        try:
            bot.polling(none_stop=True, interval=3, timeout=20)
            print('Этого не должно быть')
        except telebot.apihelper.ApiException:
            print('Проверьте связь и API')
            time.sleep(10)
        except Exception as e:
            print(e)
            time.sleep(60)


if __name__ == '__main__':
    run_bot()
