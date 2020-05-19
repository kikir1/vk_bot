import telebot
import os
import time
from telebot import types

from telebot import apihelper

apihelper.proxy = {
    'http': '165.227.121.227:80',
    'https': '142.93.176.125:8080'
}

id_group = 
token = ""

bot = telebot.TeleBot(token)

print('start')


def postMyChannel(text, photos):
    text += '\n\n<a href = "https://vk.com/skidky_ali">Источник</a>'
    if len(photos) > 1:
        bot.send_media_group(id_group, [telebot.types.InputMediaPhoto(open(photo, 'rb')) for photo in photos])
        time.sleep(1)
        doc = open(photos[0], 'rb')
        bot.send_photo(id_group, doc, text, parse_mode="HTML")
        doc.close()
    elif len(photos) == 1:
        doc = open(photos[0], 'rb')
        bot.send_photo(id_group, doc, text, parse_mode="HTML")
        doc.close()
    else:
        bot.send_message(id_group, text, parse_mode="HTML")


@bot.message_handler(commands=['start'])
def handle_start(message):
    msg = bot.send_message(id_group, "test")
