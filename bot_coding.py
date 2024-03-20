import telebot
import webbrowser
from telebot import types
import sqlite3
import requests
import json

bot = telebot.TeleBot('6858717811:AAFZGddSO-FCO40RGEcdgJs4f7gls5OotBY')
name = None
API = '41c92ecf9c2f9bc9c99219be4debdfeb'

@bot.message_handler(commands=['start'])
def main(message):
    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет, сейчас тебя зарегистрируем, введи своё имя')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован!', reply_markup=markup)


    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Узнать историю его создания', url='https://pythonist.ru/kratkaya-istoriya-yazyka-python/')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Почему люди выбирают python?', url='https://vc.ru/u/1244081-place/494001-pochemu-novichkam-sovetuyut-python')
    btn3 = types.InlineKeyboardButton('Как быстро выучить пайтон с нуля?', url='https://roadmap.sh/python')
    markup.row(btn2, btn3)
    bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.first_name} {message.from_user.last_name}!</b> Я тот самый бот, который расскажет тебе о python)', parse_mode='html')
    file = open('./photo.png', 'rb')
    bot.send_photo(message.chat.id, file, 'Что сперва ты хочешь узнать об этом языке программирования?', reply_markup=markup)
    bot.send_message(message.chat.id, 'Так же я могу показывать погоду, напиши название города!')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        feelsLike = data["main"]["feels_like"]
        min = data['main']['temp_min']
        image = 'high.png' if temp > 10.0 else 'low.jpg'
        file = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, file)
        bot.reply_to(message, f'Сейчас погода: {temp} °C \n Ощущается как: {feelsLike} °C \n Минимальная температура: {min} °C')
    else:
        bot.reply_to(message, f'Город указан неверно')
bot.polling(none_stop=True)


