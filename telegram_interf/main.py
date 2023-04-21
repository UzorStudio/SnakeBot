import time
from threading import Thread

import telebot
from telebot import types
from telebot.types import InlineKeyboardButton

import base
usrs = []
bot = telebot.TeleBot('5072194047:AAFeQRpZAloSxWP6iX2sOLKZ5suXZ_qRL2I')
db = base.Base("mongodb://Roooasr:sedsaigUG12IHKJhihsifhaosf@mongodb:27017/")


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Создать бота"))
    keyboard.add(types.KeyboardButton(text="Проверить работу"))
    usrs.append(message.chat.id)
    bot.send_message(message.chat.id, "Ку",
                     reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "Создать бота":
        bot.send_message(message.chat.id, "опишите бота по типу value_par@0.0006@test_name@0.0002@1\nВалютная_пара@общая_сумма_инвистиций@имя@сумма_инвестиций@шаг_указывать_в_сатоши")
        bot.register_next_step_handler(message, create_bot)
    elif message.text == "Проверить работу":
        for bots in db.getAllBots():
            kbrd = types.InlineKeyboardMarkup(row_width=1)
            if bots["on"] == True:
                kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
            else:
                kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

            kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))

            bot.send_message(message.chat.id,
                             f"{bots['valute_par']}\n"
                             f"{bots['name']}\n"
                             f"На балансе осталось: {bots['total_sum_invest']}\n"
                             f"Сумма инвестиций: {bots['sum_invest']}\n"
                             f"Колтичество ордеров: {len(bots['orders'])}\n"
                             f"Всего циклов: {bots['cikle_count']}\n",reply_markup=kbrd
                             )

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    msg = call.data.split("_")

    if msg[0] == 'off':
        db.offoronBot(msg[1],False)
    if msg[0] == 'on':
        db.offoronBot(msg[1],True)
    if msg[0] == 'dlt':
        db.dellBot(msg[1])

def create_bot(message):
    sp = message.text.split("@")
    db.regBot(valute_par=sp[0], total_sum_invest=float(sp[1]), name=sp[2], sum_invest=float(sp[3]), step=int(sp[4]))


def SicleSend():
    while True:
        sends = db.getSend()
        for send in sends:
            for usr in usrs:
                bot.send_message(usr,
                                 f"{send['valute_par']}\n"
                                 f"{send['name']}\n"
                                 f"Profit: {send['profit']}\n"
                                 f"Erned: {send['erned']}\n"
                                 f"Было куплено: {send['bye']}\n"
                                 f"Было продано: {send['sell']}\n"
                                 )
                db.setSend(send["_id"])
        time.sleep(3)


if __name__ == "__main__":
    while True:
        try:
            tr = Thread(target=SicleSend, args=())
            tr.start()
            bot.polling(none_stop=True)
        except Exception as e:
            # bot.send_message(5055390440,str(e))
            time.sleep(3)
            print(e)
