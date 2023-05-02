import datetime
import time

from binance.client import Client

client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2",
                "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")

def test(market):


    true_order = []

    orders = client.get_ticker()
    orders.sort(key=lambda m: float(m['bidPrice']))
    del orders[0:780]
    orders_sort_price = orders[:300]
    orders_sort_price.sort(key=lambda m: float(m['quoteVolume']),reverse = True)
    orders_sort_volume = orders_sort_price[:300]
    # print(orders_sort_price)
    for o in orders_sort_volume:
        if float(o['quoteVolume']) > 0 and float(o['bidPrice']) > 0:
            cikle = float(o['quoteVolume']) / (
                        (float(o['bidQty']) * float(o['bidPrice'])) + (float(o['askQty']) * float(o['askPrice'])))
            perc = (1-(float(o['bidPrice'])/float(o['askPrice'])))*100

            if cikle >= 10 and perc >= 0.7 and float(o['bidPrice']) <= 0.00000150:
                if len(o["symbol"].split(market)) > 1:
                    true_order.append({"symbol": o['symbol'],
                                       "askPrice": o['askPrice'],
                                       "askQty": float(o['askQty']) * float(o['askPrice']),
                                       "bidPrice": o['bidPrice'],
                                       "bidQty": float(o['bidQty']) * float(o['bidPrice']),
                                       "quoteVolume": o['quoteVolume'],
                                       "percent":perc,
                                       "cikle": cikle})
    true_order.sort(key=lambda m: m['cikle'], reverse=False)
    true_order_cikle = true_order
    true_order.sort(key=lambda m: float(m['bidPrice']), reverse=False)
    true_order_bidPrice = true_order


    return {"cikle":true_order_cikle,"price":true_order_bidPrice}

def getValute():
    cikleB = test('BTC')['cikle']
    cikleB.sort(key=lambda m: float(m['bidPrice']), reverse=True)
    cklB = cikleB
    cklB.sort(key=lambda m: float(m['quoteVolume']), reverse=False)

    cikleE = test('ETH')['cikle']
    cikleE.sort(key=lambda m: float(m['bidPrice']), reverse=True)
    cklE = cikleE
    cklE.sort(key=lambda m: float(m['quoteVolume']), reverse=False)

    return {"BTC":cklB[-10:],"ETH":cklE[-10:]}


#Сортировка по объему размещенных ордеров наверх 100%