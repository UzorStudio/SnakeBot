

from binance.client import Client

client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2",
                "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")

def test():


    true_order = []

    orders = client.get_ticker()
    orders.sort(key=lambda m: float(m['bidPrice']))
    del orders[0:780]
    orders_sort_price = orders[:100]
    orders_sort_price.sort(key=lambda m: float(m['quoteVolume']))
    orders_sort_volume = orders_sort_price[:100]
    # print(orders_sort_price)
    for o in orders_sort_volume:
        if float(o['quoteVolume']) > 0 and float(o['bidPrice']) > 0:
            cikle = float(o['quoteVolume']) / (
                        (float(o['bidQty']) * float(o['bidPrice'])) + (float(o['askQty']) * float(o['askPrice'])))

            true_order.append({"symbol": o['symbol'],
                               "askPrice": o['askPrice'],
                               "askQty": float(o['askQty']) * float(o['askPrice']),
                               "bidPrice": o['bidPrice'],
                               "bidQty": float(o['bidQty']) * float(o['bidPrice']),
                               "quoteVolume": o['quoteVolume'],
                               "cikle": cikle})

    true_order.sort(key=lambda m: (float(m['bidPrice']), m['cikle']), reverse=True)
    true_order = true_order
    for t in true_order:
        if t["cikle"] >= 1:
            print(t)


test()
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