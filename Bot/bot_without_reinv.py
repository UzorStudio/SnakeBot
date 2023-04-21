import logging
from datetime import datetime, timedelta

from binance.client import Client
from threading import Thread
import base
from time import sleep
import bin_func

client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2", "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")
db = base.Base("localhost")
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
db.UpdateSymbolInfo(client=client)

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def CheckOrder(bot_id):
    bot = db.getBot(bot_id)
    logging.info(f"check the bot: {bot['name']} ")
    for order_bye_bot in bot['orders']:
        try:
            order = client.get_order(symbol=bot['valute_par'], orderId=str(order_bye_bot))
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
                except Exception as e:
                    print(f"sell post by: {e.args} {bot['name']}")
                    pass

            bot = db.getBot(bot_id)
            if order["status"] == 'FILLED' and order["side"] == 'SELL':
                db.Sell(bot["_id"], order)
                db.dropLastPrice(bot["_id"], order)
                logging.info(f"Order {order} sold for bot {bot['name']}")

            bot = db.getBot(bot_id)
            if order["status"] == 'NEW' and order["side"] == 'SELL':
                creation_time = datetime.fromtimestamp(order["time"] / 1000)
                time_diff = datetime.now() - creation_time

                if time_diff > timedelta(hours=5):
                    logging.info(f"order time canseled: {time_diff > timedelta(hours=5)}")
                    current_price = float(client.get_avg_price(symbol=bot['valute_par'])["price"])
                    if current_price <= (float(order['price']) - 2 * bot['step']):
                        client.cancel_order(symbol=bot['valute_par'], orderId=str(order["orderId"]))
                        logging.info(
                            f"Order {order['orderId']} canceled for bot {bot['name']} due to price drop below acceptable range")
                        order_sell = bin_func.Sell(
                            quantity=order['origQty'],
                            symbol=bot['valute_par'],
                            price=current_price,
                            client=client
                        )
                        db.reloadOrderSell(bot["_id"],order,order_sell)

        except Exception as e:
            print(f"checkorder err: {e}")
            logging.error(f"{e.args} for bot {bot['name']}")



def worker():
    print("start worker")
    while True:
        try:
            bots = db.getAllBots()
            for bot in bots:
                price = client.get_avg_price(symbol=bot['valute_par'])["price"]
                if price not in bot['last_price'] and (bot["total_sum_invest"]-bot["sum_invest"]) >= 0:
                    order = bin_func.Bye(
                        client=client,
                        quantity=bot["sum_invest"],
                        symbol=bot['valute_par'],
                        price=price
                    )
                    db.addOrderBye(bot["_id"], order)
                    logging.info(f"New buy order added for bot {bot['name']} with details: {order}")
                    db.setLastPrice(bot["_id"], price)
                logging.info(f"Current price for bot {bot['name']}: {price}")
                CheckOrder(bot["_id"])
            sleep(10)
        except Exception as e:
            print(f"worker err: {e}")
            logging.exception(f"Error occurred: {e}")
            sleep(10)





if __name__ == "__main__":
    #db.regBot(valute_par="JASMYBTC",total_sum_invest=0.0006,name="TEST",sum_invest=0.0002,step=1)
    #db.regBot(valute_par="ADABTC",total_sum_invest=0.0006,name="ADABTC_TEST",sum_invest=0.0002,step=17)
    #db.regBot(valute_par="ADABTC",total_sum_invest=0.0006,name="ADABTC_fast_TEST",sum_invest=0.0002,step=7)
    #db.regBot(valute_par="DOGEBTC",total_sum_invest=0.009,name="DOGEBTC_fast3_009_TEST",sum_invest=0.00011,step=3)
    #db.regBot(valute_par="DOGEBTC",total_sum_invest=0.0010,name="DOGEBTC_fast2_TEST",sum_invest=0.0002,step=2)
    #db.regBot(valute_par="DOGEBTC",total_sum_invest=0.0010,name="DOGEBTC_fast3_TEST",sum_invest=0.0002,step=3)
    #db.regBot(valute_par="LTOBTC",total_sum_invest=0.0006,name="LTOBTC_fast1_TEST",sum_invest=0.00021,step=3)
    #db.regBot(valute_par="LTOBTC",total_sum_invest=0.0006,name="LTOBTC_fast2_TEST",sum_invest=0.00021,step=4)
    tr = Thread(target=worker, args=(), name="Main_Worker")
    tr.start()