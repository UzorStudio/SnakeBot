import logging
from datetime import datetime, timedelta

from binance.client import Client
from threading import Thread
import base
from time import sleep
import bin_func

#client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2", "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")
client = Client("ovaDkCgIRhRrZKmi3Ylrv7YzQojGWGbDDZJ8UmgkgDC2A68tv0KNDa1m1nWubSwA", "MrGVvzbgdkXO4hsVwb0yXj2w1fbmSZzUBOpyx06eq5UMdAF0yUhv3Ov8UKD7BVBR")
#db = base.Base("localhost")
db = base.Base("mongodb://Roooasr:sedsaigUG12IHKJhihsifhaosf@mongodb:27017/")
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
db.UpdateSymbolInfo(client=client)

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


def cancleBye(bot,order):
    if order["status"] == 'NEW' and order["side"] == 'BUY':
        creation_time = datetime.fromtimestamp(order["time"] / 1000)
        time_diff = datetime.now() - creation_time
        if time_diff > timedelta(hours=2):
            current_price = float(client.get_avg_price(symbol=bot['valute_par'])["price"])

            if (float(order['price']) + 2 * bot['step']) < current_price:
                client.cancel_order(symbol=bot['valute_par'], orderId=str(order["orderId"]))
                logging.info(
                    f"Order {order['orderId']} canceled for bot {bot['name']}c drop below acceptable range")
                db.dropLastPriceBye(bot["_id"], order)
                db.reloadSumInvest(bot["_id"], order)
                bot = db.getBot(bot["_id"])

                if current_price not in bot['last_price'] and (
                        bot["total_sum_invest"] - float(order['origQty'])*float(order['price'])) >= 0:
                    # Менять ордербайид в ордере бота
                    try:
                        order_new = bin_func.Bye(
                            client=client,
                            quantity=float(order['origQty'])*float(order['price']),
                            symbol=bot['valute_par'],
                            price=current_price
                        )
                        db.reloadOrderBye(bot["_id"], order, order_new)
                        logging.info(f"New REBYE for bot {bot['name']} with details: {order_new}")
                        db.setLastPrice(bot["_id"], current_price)
                    except Exception as e:
                        print(f"Error CANCELED BYE: {e.args} {bot['name']} {order}")
                        logging.error(f"Error CANCELED BYE: {e.args} {bot['name']} {order}")


def cancleSell(bot, order):
    if order["status"] == 'NEW' and order["side"] == 'SELL':
        creation_time = datetime.fromtimestamp(order["time"] / 1000)
        time_diff = datetime.now() - creation_time
        if time_diff > timedelta(hours=10):
            currentprice = client.get_avg_price(symbol=bot['valute_par'])["price"]
            current_price = float(currentprice)

            if (float(order['price']) + 2 * bot['step']) > current_price and bot["bye_order"] != True:

                balance = client.get_asset_balance(db.GetSymbolInfo(bot['valute_par'])['quoteAsset'])

                try:
                    if float(balance['free']) - float(bot['full_orders'][currentprice]) >= 0:
                        return 0
                except:
                    pass

                if float(balance['free']) - bot['sum_invest'] >= 0:
                    return 0




                client.cancel_order(symbol=bot['valute_par'], orderId=str(order["orderId"]))
                logging.info(
                    f"Order {order['orderId']} SELL canceled for bot {bot['name']}c drop below acceptable range")

                bot = db.getBot(bot["_id"])

                try:
                    # Может быть стоит переписать ордер внутри бота. Пусть показывает минус
                    order_new = bin_func.Sell(
                        client=client,
                        quantity=order['origQty'],
                        symbol=bot['valute_par'],
                        price=currentprice
                    )
                    db.reloadSell(bot["_id"], order, order_new)
                    logging.info(f"New CANCELED for bot {bot['name']} with details: {order_new}")
                except Exception as e:
                    print(f"Error CANCELED SELL: {e.args} {bot['name']}")
                    logging.info(f"Error CANCELED SELL: {e.args} {bot['name']} {order}")


def CheckOrder(bot_id):
    bot = db.getBot(bot_id)
    #logging.info(f"check the bot: {bot['name']} ")
    for order_bye_bot in bot['orders']:

        order = client.get_order(symbol=bot['valute_par'], orderId=str(order_bye_bot))

        if order["status"] == 'CANCELED' and order["side"] == 'SELL':
            print(order)
            db.dropLastPriceSell(bot['_id'],order)
            continue

        if order["status"] == 'CANCELED' and order["side"] == 'BUY':
            print(order)
            db.dropLastPriceBye(bot["_id"], order)
            db.reloadSumInvest(bot["_id"], order)
            db.dropOrder(bot["_id"],order)
            continue

        if order["status"] == 'FILLED' and order["side"] == 'BUY':
            #Продажа в случае покупки
            try:
                order_sell = bin_func.Sell(
                    quantity=order['origQty'],
                    symbol=bot['valute_par'],
                    price='{:.8f}'.format(float(order["price"])+bot['step']),
                    client=client
                )
                db.addOrderSell(bot["_id"], order, order_sell)
                logging.info(f"New sell order added for bot {bot['name']} with details: {order_sell}")
                continue
            except Exception as e:
                print(f"Error post BUY: {e.args} {bot['name']} {order}")
                logging.info(f"Error post BUY: {e.args} {bot['name']} {order}")


        bot = db.getBot(bot_id)
        if order["status"] == 'FILLED' and order["side"] == 'SELL':
            db.Sell(bot["_id"], order)
            db.dropLastPrice(bot["_id"], order)
            bot = db.getBot(bot_id)
            logging.info(f"Order {order} sold for bot {bot['name']}")
            price = '{:.8f}'.format(float(order["price"]) - bot['step'])
            if price not in bot['last_price']:
                # Покупка в случае продажи
                if bot['reinvest'] == True:
                    try:
                        print(f"order on reinvest: {order}")
                        order = bin_func.Bye(
                            client=client,
                            quantity=order['cummulativeQuoteQty'],
                            symbol=bot['valute_par'],
                            price= price
                        )

                        if order != 0:
                            db.addOrderBye(bot["_id"], order)
                            logging.info(f"New REINVEST for bot {bot['name']} with details: {order}")
                            db.setLastPrice(bot["_id"], price)
                        else:
                            continue
                        continue
                    except Exception as e:
                        print(f"Error reinvest Bye post SELL: {e.args} {bot['name']} {order}")
                        logging.info(f"Error reinvest Bye post SELL: {e.args} {bot['name']} {order}")
                elif bot['reinvest'] == False:
                    try:
                        print(f"order on reinvest: {order}")
                        order = bin_func.Bye(
                            client=client,
                            quantity=bot["sum_invest"],
                            symbol=bot['valute_par'],
                            price=price
                        )

                        if order != 0:
                            db.addOrderBye(bot["_id"], order)
                            logging.info(f"New Bye for bot {bot['name']} with details: {order}")
                            db.setLastPrice(bot["_id"], price)
                        else:
                            continue
                        continue
                    except Exception as e:
                        print(f"Error non reinvest Bye post SELL: {e.args} {bot['name']} {order}")
                        logging.info(f"Error non reinvest Bye post SELL: {e.args} {bot['name']} {order}")
                elif bot['reinvest'] == 3:
                    try:
                        print(f"order on 50 reinvest: {order}")
                        inv = db.reinv50Math(order)

                        order = bin_func.Bye(
                            client=client,
                            quantity=inv["inv_sum"],
                            symbol=bot['valute_par'],
                            price=price
                        )

                        if order != 0:
                            client.transfer_spot_to_margin(asset='BTC', amount=inv['profit'])
                            db.addOrderBye(bot["_id"], order)
                            logging.info(f"New Bye for bot {bot['name']} with details: {order}")
                            db.setLastPrice(bot["_id"], price)
                        else:
                            continue
                        continue
                    except Exception as e:
                        print(f"Error 50 reinvest Bye post SELL: {e.args} {bot['name']} {order}")
                        logging.info(f"Error 50 Bye post SELL: {e.args} {bot['name']} {order}")


        #Системная отмена ордера на покупку
        bot = db.getBot(bot_id)
        cancleBye(bot,order)



        #Отмена ордера на продажу
        #bot = db.getBot(bot_id)
        #cancleSell(bot,order)


def worker():
    print("start worker")
    while True:
        try:
            bots = db.getAllBots()

            for bot in bots:
                if bot["on"] == True:
                    CheckOrder(bot["_id"])
                    price = client.get_avg_price(symbol=bot['valute_par'])["price"]
                    if price not in bot['last_price'] and (float(price)-bot['step']) <= bot['max_price'] and float(price) >= bot['min_price']:

                        if float(bot['last_price'][-1]) - bot['step'] > float(price):
                            break

                        try:
                            if bot['reinvest'] == True:
                                if price in str(bot['full_orders']):
                                    order_bye = bin_func.Bye(
                                        client=client,
                                        quantity=bot['full_orders'][price],
                                        symbol=bot['valute_par'],
                                        price=price
                                    )
                                else:
                                    if (bot["total_sum_invest"] - bot["sum_invest"]) < 0:
                                        try:
                                            order_bye = bin_func.Bye(
                                                client=client,
                                                quantity=bot['total_sum_invest'],
                                                symbol=bot['valute_par'],
                                                price=price
                                            )
                                        except:
                                            order_bye = 0
                                    else:
                                        order_bye = bin_func.Bye(
                                            client=client,
                                            quantity=bot['sum_invest'],
                                            symbol=bot['valute_par'],
                                            price=price
                                        )
                            elif bot['reinvest'] == False:
                                if (bot["total_sum_invest"] - bot["sum_invest"]) < 0:
                                    try:
                                        order_bye = bin_func.Bye(
                                            client=client,
                                            quantity=bot['total_sum_invest'],
                                            symbol=bot['valute_par'],
                                            price=price
                                        )
                                    except:
                                        order_bye = 0
                                else:
                                    order_bye = bin_func.Bye(
                                        client=client,
                                        quantity=bot['sum_invest'],
                                        symbol=bot['valute_par'],
                                        price=price
                                    )

                            elif bot['reinvest'] == 3:
                                if price in str(bot['full_orders']):
                                    order_bye = bin_func.Bye(
                                        client=client,
                                        quantity=bot['full_orders'][price],
                                        symbol=bot['valute_par'],
                                        price=price
                                    )
                                else:
                                    if (bot["total_sum_invest"] - bot["sum_invest"]) < 0:
                                        try:
                                            order_bye = bin_func.Bye(
                                                client=client,
                                                quantity=bot['total_sum_invest'],
                                                symbol=bot['valute_par'],
                                                price=price
                                            )
                                        except:
                                            order_bye = 0
                                    else:
                                        order_bye = bin_func.Bye(
                                            client=client,
                                            quantity=bot['sum_invest'],
                                            symbol=bot['valute_par'],
                                            price=price
                                        )
                            else:
                                order_bye = 0
                            #print(order)
                            if order_bye != 0:
                                db.addOrderBye(bot["_id"], order_bye)
                                logging.info(f"New buy order added for bot {bot['name']} with details: {order_bye}")
                                db.setLastPrice(bot["_id"], price)
                            else:
                                pass
                                #print(f"None balance on bank for bot {bot['name']}: {price}")
                                #logging.info(f"None balance on bank for bot {bot['name']}: {price}")
                        except Exception as e:
                            print(e.args)
                    #logging.info(f"Current price for bot {bot['name']}: {price}")
                    sleep(10)
        except Exception as e:
            print(f"worker err: {e}")
            logging.exception(f"Error occurred: {e} {bot}")
            sleep(10)





if __name__ == "__main__":
    #db.regBot(valute_par="TRXBTC",total_sum_invest=0.001,name="TEST_TRXBTC",sum_invest=0.0005,step=1)
    tr = Thread(target=worker, args=(), name="Main_Worker")
    tr.start()