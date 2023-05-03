import datetime
import time

from binance.client import Client

from Bot import base

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

            if cikle >= 10 and float(o['bidPrice']) <= 0.00000150:
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

    return {"BTC":cklB,"ETH":cklE}


#Сортировка по объему размещенных ордеров наверх 100%

#v = getValute()['BTC']
#for i in v:
#    print(i)

strtInv = 10
strt = strtInv

for i in range(20):
    strtInv = strtInv +(strtInv*0.01)

print(strtInv,(1-(strt/strtInv))*100)

#db = base.Base("localhost")


def getPrice(symbol):
    tick = client.get_ticker(symbol=symbol)
    bidQty = float(tick['bidQty'])*float(tick['bidPrice'])


    return {'price_bye':tick['bidPrice'],'bye_qty':bidQty}

#print(getPrice('OMBTC')['bye_qty']/0.0002,getPrice('OMBTC'))
def pr(price,symbol):
    trades = []
    summ = 0
    tick = client.get_orderbook_ticker(symbol=symbol)
    print(tick)
    for t in tick['symbol']:
        print(t)
        if t['price'] == price:
            trades.append(t)
            print(datetime.datetime.fromtimestamp(t['time']/1000))
            summ+=float(t['qty'])*float(t['price'])


    return {"count":len(trades),"sum":summ}



    #td = client.get_all_orders(symbol='DOGEBTC')
#
#print(td[0])
#for t in td:
#    if t['orderId'] == 461247475 or t['orderId'] == 461269941 or t['orderId'] == 461482670:
#        print(td)

#for o in orders:
#
#    print(o)
#    print(f"o['askPrice']: {o['askPrice']}")
#    print(f"askQty: {float(o['askQty']) * float(o['askPrice'])}")
#    print(f"o['bidPrice']: {o['bidPrice']}")
#    print(f"bidQty: {float(o['bidQty'])*float(o['bidPrice'])}")
#    print(f"quoteVolume: {o['quoteVolume']}")
#    print(o['count'])



#mass = [{"num":3,"prof":0.1},{"num":1,"prof":0.2},{"num":2,"prof":0.3}]
#
#mass.sort(key=lambda m: m['num'])
#mass.sort(key=lambda m: m['prof'], reverse=True)
#
#print(mass)