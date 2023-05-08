import time
from threading import Thread
import get_all
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton

import base
usrs = []
bot = telebot.TeleBot('5072194047:AAFeQRpZAloSxWP6iX2sOLKZ5suXZ_qRL2I')
db = base.Base("mongodb://Roooasr:sedsaigUG12IHKJhihsifhaosf@mongodb:27017/")
#db = base.Base("localhost")


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Создать бота"))
    keyboard.add(types.KeyboardButton(text="Проверить работу"))
    keyboard.add(types.KeyboardButton(text="Посмотреть топ пар"))
    if message.chat.id not in usrs:
        usrs.append(message.chat.id)
    print(usrs)
    bot.send_message(message.chat.id, "Ку",
                     reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "Создать бота":
        bot.send_message(message.chat.id, "опишите бота по типу:\nvalue_par@0.0006@test_name@0.0002@1@0.00000021@0.00000022\nВалютная_пара@общая_сумма_инвистиций@имя@сумма_инвестиций@шаг_указывать_в_сатоши@мин_цена@макс_цена")
        bot.register_next_step_handler(message, create_bot)
    elif message.text == "Проверить работу":
        for bots in db.getAllBots():
            kbrd = types.InlineKeyboardMarkup(row_width=1)
            if bots["on"] == True:
                kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
            else:
                kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

            if bots["reinvest"] == True:
                kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
                kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
            elif bots["reinvest"] == False:
                kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
                kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
            elif bots["reinvest"] == 3:
                kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

            kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))



            bot.send_message(message.chat.id,
                             f"{bots['valute_par']}\n"
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"
                             f"На балансе осталось: {bots['total_sum_invest']}\n"
                             f"Заработано ботом: {bots['earned']}\n"
                             f"Сумма инвестиций: {bots['sum_invest']}\n"
                             f"Колтичество ордеров: {len(bots['orders'])}\n"
                             f"Всего циклов: {bots['cikle_count']}\n",reply_markup=kbrd
                             )
    elif message.text == "Посмотреть топ пар":
        parss = get_all.getValute()['BTC']

        for pars in parss:
            bot.send_message(message.chat.id,
                             f"{pars['symbol']}\n"
                             f"Цена: {toFixed(float(pars['askPrice']), 8)}-{toFixed(float(pars['bidPrice']), 8)}\n"
                             f"Общий объем: {pars['quoteVolume']}\n"
                             f"Доходность: {pars['percent']}\n"
                             f"Кол-во циклов 24ч: ~{toFixed(float(pars['cikle']), 2)}\n"
                             f"https://www.binance.com/ru/trade/{pars['symbol']}"
                             )

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    msg = call.data.split("_")

    if msg[0] == 'off':

        db.offoronBot(msg[1],False)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n"\
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"\
                             f"На балансе осталось: {bots['total_sum_invest']}\n"\
                             f"Заработано ботом: {bots['earned']}\n"\
                             f"Сумма инвестиций: {bots['sum_invest']}\n"\
                             f"Колтичество ордеров: {len(bots['orders'])}\n"\
                             f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt, reply_markup=kbrd)
    if msg[0] == 'on':
        db.offoronBot(msg[1],True)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n"\
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"\
                             f"На балансе осталось: {bots['total_sum_invest']}\n"\
                             f"Заработано ботом: {bots['earned']}\n"\
                             f"Сумма инвестиций: {bots['sum_invest']}\n"\
                             f"Колтичество ордеров: {len(bots['orders'])}\n"\
                             f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                              reply_markup=kbrd)
    if msg[0] == 'offr':
        db.offoronReivest(msg[1],False)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n"\
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"\
                             f"На балансе осталось: {bots['total_sum_invest']}\n"\
                             f"Заработано ботом: {bots['earned']}\n"\
                             f"Сумма инвестиций: {bots['sum_invest']}\n"\
                             f"Колтичество ордеров: {len(bots['orders'])}\n"\
                             f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                              reply_markup=kbrd)
    if msg[0] == 'onr':
        db.offoronReivest(msg[1],True)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n"\
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"\
                             f"На балансе осталось: {bots['total_sum_invest']}\n"\
                             f"Заработано ботом: {bots['earned']}\n"\
                             f"Сумма инвестиций: {bots['sum_invest']}\n"\
                             f"Колтичество ордеров: {len(bots['orders'])}\n"\
                             f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                              reply_markup=kbrd)
    if msg[0] == 'on50r':
        db.offoronReivest(msg[1], 3)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n" \
              f"{bots['name']} {toFixed(bots['min_price'], 8)}-{toFixed(bots['max_price'], 8)}\n" \
              f"На балансе осталось: {bots['total_sum_invest']}\n" \
              f"Заработано ботом: {bots['earned']}\n" \
              f"Сумма инвестиций: {bots['sum_invest']}\n" \
              f"Колтичество ордеров: {len(bots['orders'])}\n" \
              f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                              reply_markup=kbrd)
    if msg[0] == 'on50r':
        db.offoronReivest(msg[1], True)
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n" \
              f"{bots['name']} {toFixed(bots['min_price'], 8)}-{toFixed(bots['max_price'], 8)}\n" \
              f"На балансе осталось: {bots['total_sum_invest']}\n" \
              f"Заработано ботом: {bots['earned']}\n" \
              f"Сумма инвестиций: {bots['sum_invest']}\n" \
              f"Колтичество ордеров: {len(bots['orders'])}\n" \
              f"Всего циклов: {bots['cikle_count']}\n"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                              reply_markup=kbrd)
    if msg[0] == 'dlt':
        db.dellBot(msg[1])

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Удален")
    if msg[0] == 'upd':
        bots = db.getBot(msg[1])

        kbrd = types.InlineKeyboardMarkup(row_width=1)
        if bots["on"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить", callback_data=f"off_{str(bots['_id'])}"))
        else:
            kbrd.add(InlineKeyboardButton(text="Включить", callback_data=f"on_{str(bots['_id'])}"))

        if bots["reinvest"] == True:
            kbrd.add(InlineKeyboardButton(text="Выключить Реинвест", callback_data=f"offr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == False:
            kbrd.add(InlineKeyboardButton(text="Включить Реинвест", callback_data=f"onr_{str(bots['_id'])}"))
            kbrd.add(InlineKeyboardButton(text="Включить 50 Реинвест", callback_data=f"on50r_{str(bots['_id'])}"))
        elif bots["reinvest"] == 3:
            kbrd.add(InlineKeyboardButton(text="Выключить 50 Реинвест", callback_data=f"off50r_{str(bots['_id'])}"))

        kbrd.add(InlineKeyboardButton(text="Удалить", callback_data=f"dlt_{str(bots['_id'])}"))
        kbrd.add(InlineKeyboardButton(text="Обновить инф.", callback_data=f"upd_{str(bots['_id'])}"))
        txt = f"{bots['valute_par']}\n"\
                             f"{bots['name']} {toFixed(bots['min_price'],8)}-{toFixed(bots['max_price'],8)}\n"\
                             f"На балансе осталось: {bots['total_sum_invest']}\n"\
                             f"Заработано ботом: {bots['earned']}\n"\
                             f"Сумма инвестиций: {bots['sum_invest']}\n"\
                             f"Колтичество ордеров: {len(bots['orders'])}\n"\
                             f"Всего циклов: {bots['cikle_count']}\n"
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt,
                                  reply_markup=kbrd)
        except:
            pass

def create_bot(message):
    sp = message.text.split("@")
    db.regBot(valute_par=sp[0], total_sum_invest=float(sp[1]), name=sp[2], sum_invest=float(sp[3]), step=int(sp[4]),min_price=float(sp[5]),max_price=float(sp[6]))


def SicleSend():
    print("sicle start")
    print(len(usrs))
    while True:
        sends = db.getSend()
        for send in sends:
            print(send)
            for usr in usrs:
                bot.send_message(usr,
                                 f"{send['valute_par']}\n"
                                 f"{send['bot']}\n"
                                 f"Profit: {send['profit']}%\n"
                                 f"Erned: {send['erned']}\n"
                                 f"Было куплено: {send['bye']}\n"
                                 f"По цене: {send['price_bye']}\n"
                                 f"Было продано: {send['sell']}\n"
                                 f"По цене: {send['price_sell']}\n"
                                 )
                db.setSend(send["_id"])
        time.sleep(3)


if __name__ == "__main__":
    tr = Thread(target=SicleSend, args=())
    tr.start()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            # bot.send_message(5055390440,str(e))
            time.sleep(3)
            print(e)
